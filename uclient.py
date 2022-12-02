from socket import *
from threading import Thread
import random
import time
import sys
import math
import matplotlib.pyplot as plt
import numpy as np

serverIP = '127.0.0.1' # special IP for local host
serverPort = 12000
clientPort = 12001

# win = 10      # window size
win = 1 # window size for slow start
ssthresh = 16 # if window size exceeds this threshold, slow start ends

no_pkt = 1000 # the total number of packets to send
send_base = 0 # oldest packet sent
loss_rate = 0.01 # loss rate
seq = 0        # initial sequence number
timeout_flag = 0 # timeout trigger

loss_flag = False # True if loss is detected

triple_flag = 0 # triple duplicate ACK trigger
ack_queue = [] # ack queue. if the queue is full(len = 3), -> triple duplicate ACK
how_many_retransmission_by_triple = 0
how_many_retransmission_by_timeout = 0

triple_ack = 0 # triple duplicate으로 온 그 ack 저장

sent_time = [0 for i in range(2000)]

window_size_history = []
ack_history = []

temp_flag = True


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', clientPort))
clientSocket.setblocking(0)

# def check_queue_if_duplicate (list):
#     if len(list) == 0:
#         return False
#     if len(list)  0:
        

# thread for receiving and handling acks
def handling_ack():
    print("thread")
    global clientSocket
    global send_base
    global timeout_flag
    global sent_time
    
    global triple_flag
    global ack_queue
    global how_many_retransmission_by_triple
    global loss_flag
    global win
    global ssthresh
    global window_size_history
    global triple_ack
    global ack_history
    global temp_flag

    alpha = 0.125
    beta = 0.25
    timeout_interval = 10  # timeout interval

    
    pkt_delay = 0
    dev_rtt = 0
    init_rtt_flag = 1    
    
    
    while True:
       
        if sent_time[send_base] != 0: 
            pkt_delay = time.time() - sent_time[send_base]
     
            
        if pkt_delay > timeout_interval and timeout_flag == 0:    # timeout detected
            print("timeout detected:", str(send_base), flush=True)
            print("timeout interval:", str(timeout_interval), flush=True)
            timeout_flag = 1
            loss_flag = True
            win = math.ceil(win / 2)
            ack_history.append(send_base)
            window_size_history.append(win)
            # print("win size:", win)
            win = 1
            # window_size_history.append(win)
            
            
            
            
        if len(ack_queue) == 3 and ack_queue[0] == ack_queue[1] and ack_queue[1] == ack_queue[2]:
            triple_ack = ack_queue[1]
            print("triple detected (send_base, ack):", str(send_base), triple_ack ,flush=True)
            # print("duplciate ACK:", str(ack_queue[0]), flush=True)
            triple_flag = 1
            loss_flag = True
            win = math.ceil(win / 2)
            ack_history.append(send_base)
            window_size_history.append(win)
            print("win size:", win)
            # win = 1
            # window_size_history.append(win)
            ack_queue = []

        try:
            ack, serverAddress = clientSocket.recvfrom(2048)
            ack_n = int(ack.decode())
            # if win < ssthresh:
            #     win += 2
            # else:
            #     win += 1
            if win < ssthresh:
                win += 1
            else:
                if ack_n == send_base + win - 1:
                    win += 1
            window_size_history.append(win)
            print(ack_n, flush=True)
            ack_history.append(ack_n)
            
            """
            여기 ack_n을 ack_queue에 넣어야 됨!
            ack_queue의 길이가 3 이상인데 더 넣지 않도록 주의
            """
            if ack_n != triple_ack:
                if len(ack_queue) == 0:
                    if triple_flag == False:
                        ack_queue.append(ack_n)
                elif len(ack_queue) > 0 and len(ack_queue) < 3:
                    if ack_queue[-1] == ack_n:
                        ack_queue.append(ack_n)
                    else:
                        ack_queue = []
                  
            if init_rtt_flag == 1:
                estimated_rtt = pkt_delay
                init_rtt_flag = 0
            else:
                estimated_rtt = (1-alpha)*estimated_rtt + alpha*pkt_delay
                dev_rtt = (1-beta)*dev_rtt + beta*abs(pkt_delay-estimated_rtt)
            timeout_interval = estimated_rtt + 4*dev_rtt
            #print("timeout interval:", str(timeout_interval), flush=True)

            
        except BlockingIOError:
            continue
            
        # window is moved upon receiving a new ack
        # window stays for cumulative ack
        if ack_n + 1 >= send_base:
            send_base = ack_n + 1
        # send_base = ack_n + 1  
        
        if ack_n == 999:
            print("ack_999 break")
            temp_flag = False
            break

# running a thread for receiving and handling acks
th_handling_ack = Thread(target = handling_ack, args = ())
th_handling_ack.start()

# while seq < no_pkt:
while temp_flag:
    while seq < send_base + win: # send packets within window
        # if random.random() < 1 - loss_rate: # emulate packet loss
            # clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))  
        if loss_flag == False:
            clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()    
        seq = seq + 1
        
            
        
    if timeout_flag == 1: # retransmission
        # if triple_flag == False:
        seq = send_base 
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()
        print("retransmission:", str(seq), flush=True)
        seq = seq + 1
        timeout_flag = 0
        how_many_retransmission_by_timeout += 1
        loss_flag = False
        
    if triple_flag == 1: # retransmission by triple duplicate ACK
        
        seq = send_base
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        ack_queue = []
        loss_flag = False
        sent_time[seq] = time.time()
        print("retransmission_triple:", str(seq), flush=True)
        seq = seq + 1
        triple_flag = 0
        how_many_retransmission_by_triple += 1
        
print("seq:", seq) 
print("send_base:", send_base) 
print("window size:", win)
print("while done")
# sys.exit(0)
th_handling_ack.join() # terminating thread

print ("done")
print("re by triple:", how_many_retransmission_by_triple)
print("re by timeout:", how_many_retransmission_by_timeout)
print("window size:", win)

clientSocket.close()

plt.plot(np.transpose(ack_history) , np.transpose(window_size_history), 'k')
plt.savefig('temp.png')