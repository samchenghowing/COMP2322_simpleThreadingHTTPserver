#!/usr/bin/python
# https://www.tutorialspoint.com/python/python_multithreading.htm
# https://stackoverflow.com/questions/17453212/multi-threaded-tcp-server-in-python
from socket import *
from datetime import date
import threading, logging

class clientThread(threading.Thread):

    def __init__(self,ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        writeLog("[+] New thread started for "+ip+":"+str(port))

    def run(self):
        writeLog("Connection from : " +ip + ":" + str(port))
        self.socket.send("\nWelcome to the server")
        data = self.socket.recv(1024)
        writeLog("Received from " + ip + ":" + str(port) + ": " + data)


        self.socket.send("\nbye")
        writeLog("Client disconnected..., killing this thread")
        self.socket.close()

def initLogger():
    today = date.today()
    logging.basicConfig(filename=(today.strftime("%d%m%y")+"connectionLog.txt"),
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)
    logging.getLogger('HTTPServer').info("The logger is initialized, program started")

def writeLog(logStr):
    logging.getLogger('HTTPServer').info(logStr)

initLogger()
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(("", serverPort)) #blind to local IP 
threads = []

while True:
    serverSocket.listen(4)
    print ("\nListening for incoming connections...")
    (clientsock, (ip, port)) = serverSocket.accept()
    newthread = clientThread(ip, port, clientsock)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()