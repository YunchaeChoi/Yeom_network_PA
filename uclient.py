from socket import *
from threading import Thread
import random
import time

serverIP = '127.0.0.1' # special IP for local host
serverPort = 12000
clientPort = 12001

win = 10      # window size
no_pkt = 1000 # the total number of packets to send
send_base = 0 # oldest packet sent
loss_rate = 0.01 # loss rate
seq = 0        # initial sequence number
timeout_flag = 0 # timeout trigger

triple_flag = 0 # triple duplicate ACK trigger
ack_queue = [] # ack queue. if the queue is full(len = 3), -> triple duplicate ACK
how_many_retransmission_by_triple = 0
how_many_retransmission_by_timeout = 0

sent_time = [0 for i in range(2000)]


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
            
        if len(ack_queue) == 3 and ack_queue[0] == ack_queue[1] and ack_queue[1] == ack_queue[2]:
            print("triple duplicate ACK detected:", str(send_base), flush=True)
            # print("duplciate ACK:", str(ack_queue[0]), flush=True)
            triple_flag = 1

        try:
            ack, serverAddress = clientSocket.recvfrom(2048)
            ack_n = int(ack.decode())
            print(ack_n, flush=True)
            
            """
            여기 ack_n을 ack_queue에 넣어야 됨!
            ack_queue의 길이가 3 이상인데 더 넣지 않도록 주의
            """
            
            if len(ack_queue) == 0:
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
        send_base = ack_n + 1
        
        if ack_n == 999:
            break

# running a thread for receiving and handling acks
th_handling_ack = Thread(target = handling_ack, args = ())
th_handling_ack.start()

while seq < no_pkt:
    while seq < send_base + win: # send packets within window
        if random.random() < 1 - loss_rate: # emulate packet loss
            clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))  
        sent_time[seq] = time.time()    
        seq = seq + 1
        
    if timeout_flag == 1: # retransmission
        seq = send_base 
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()
        print("retransmission:", str(seq), flush=True)
        seq = seq + 1
        timeout_flag = 0
        how_many_retransmission_by_timeout += 1
        
    if triple_flag == 1: # retransmission by triple duplicate ACK
        seq = send_base
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()
        print("retransmission_triple:", str(seq), flush=True)
        seq = seq + 1
        triple_flag = 0
        how_many_retransmission_by_triple += 1
        
        
th_handling_ack.join() # terminating thread

print ("done")
print("re by triple:", how_many_retransmission_by_triple)
print("re by timeout:", how_many_retransmission_by_timeout)

clientSocket.close()

