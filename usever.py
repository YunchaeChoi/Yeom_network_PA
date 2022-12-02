from socket import *
from threading import Thread
import time
from queue import Queue
# from threading import Lock
import random

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
start_time = time.time()

print('The server is ready to receive')

rcv_base = 0  # next sequence number we wait for

queue_max_size = 20
loss_rate = 0.9

queue = Queue() # queue that stores acks
clientAddress = None
# flag_recving_sending = 0 # if 0, recving's turn. if 1, sending's turn

done_flag = False
pkt_delay = 0
last_recv_time = 0


receive_count = 0

# thread for receiving and queueing packets
def recving():
    global rcv_base
    global serverSocket
    global queue
    global clientAddress
    global done_flag
    global receive_count
    global pkt_delay
    global last_recv_time
    
    while True:
        if done_flag == True:
            print("recving thread break!!")
            break
        if rcv_base == 1000:
            break
            
        print("try to receive")
        message, clientAddress = serverSocket.recvfrom(2048)
        seq_n = int(message.decode()) # extract sequence number
        print(seq_n)
        time_now  = time.time()
        if last_recv_time:
            pkt_delay = time_now - last_recv_time
        else:
            pkt_delay = time.time() - time_now
        last_recv_time = time_now
        
        if queue.qsize() < queue_max_size:
            queue.put(seq_n)
            
        
        
th_recving = Thread(target = recving, args = ())
th_recving.start()

while True:
    seq_n = queue.get()
    if seq_n >= rcv_base: # in order delivery
        rcv_base = seq_n + 1 
    time.sleep(pkt_delay * (loss_rate))
    print("q size, rcv_base, seq_n:", queue.qsize(), rcv_base, seq_n)
    serverSocket.sendto(str(rcv_base-1).encode(), clientAddress) # send cumulative ack
    # if seq_n == 999:
    if rcv_base == 1000:
        print("main thread break")
        break

done_flag = True
serverSocket.close()
print("done")
print("Elapsed time:", time.time() - start_time)