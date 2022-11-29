from socket import *
from threading import Thread
import time
from queue import Queue
# from threading import Lock

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print('The server is ready to receive')

rcv_base = 0  # next sequence number we wait for

queue = Queue(10) # queue that stores acks
clientAddress = None
# flag_recving_sending = 0 # if 0, recving's turn. if 1, sending's turn

done_flag = False

# thread for receiving and queueing packets
def recving():
    global rcv_base
    global serverSocket
    global queue
    global clientAddress
    global done_flag
    # global flag_recving_sending
    
    while True:
        if done_flag == True:
            print("recving thread break!!")
            break
        print("try to receive")
        message, clientAddress = serverSocket.recvfrom(2048)
        seq_n = int(message.decode()) # extract sequence number
        print(seq_n)
        
        if queue.qsize() < 10:
            # if seq_n < 1000:
            queue.put(seq_n)
            # else:
            #     break
            
# # thread for sending acks
# def sending():
#     global rcv_base
#     global serverSocket
#     global queue
#     global clientAddress
#     # global flag_recving_sending
    
#     while True:
#         if queue.qsize() > 3:
#             seq_n = queue.get()
#             print("GET!!")
#             if seq_n == rcv_base: # in order delivery
#                 rcv_base = seq_n + 1 
#             serverSocket.sendto(str(rcv_base-1).encode(), clientAddress) # send cumulative ack
#             if seq_n == 999:
#                 break
        
th_recving = Thread(target = recving, args = ())
th_recving.start()
# th_sending = Thread(target= sending, args = ())
# th_sending.start()

while True:
    time.sleep(0.0002)
    seq_n = queue.get()
    print("GET!!")
    if seq_n == rcv_base: # in order delivery
        rcv_base = seq_n + 1 
    print("q size, rcv_base:", queue.qsize(), rcv_base)
    serverSocket.sendto(str(rcv_base-1).encode(), clientAddress) # send cumulative ack
    # if seq_n == 999:
    if rcv_base == 1000:
        print("main thread break")
        break

print("donedoneondeondoneondondonoendoneodnodnoen")
done_flag = True
serverSocket.close()
print("EOF")















# from socket import *

# serverPort = 12000

# serverSocket = socket(AF_INET, SOCK_DGRAM)
# serverSocket.bind(('', serverPort))

# print('The server is ready to receive')

# rcv_base = 0  # next sequence number we wait for

# while True:
#     message, clientAddress = serverSocket.recvfrom(2048)
#     seq_n = int(message.decode()) # extract sequence number
#     print(seq_n)
#     if seq_n == rcv_base: # in order delivery
#         rcv_base = seq_n + 1 
#     serverSocket.sendto(str(rcv_base-1).encode(), clientAddress) # send cumulative ack
#     if seq_n == 999:
#         break

# serverSocket.close()


