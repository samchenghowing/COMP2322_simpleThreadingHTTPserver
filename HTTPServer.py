#!/usr/bin/python
# https://www.tutorialspoint.com/python/python_multithreading.htm
# https://stackoverflow.com/questions/17453212/multi-threaded-tcp-server-in-python
from socket import *
from datetime import date
import threading, logging

class clientThread(threading.Thread):
    """This class is use to create a client thread for a HTTP connection"""

    def __init__(self, ip, port, socket):
        """Overriding the thread init funtion, added ip, port, socket parameter for this thread"""
        
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        logging.getLogger('ThreadingHTTPServer').info("[+] New thread started for "+ip+":"+str(port))

    def run(self):
        """Overriding the thread run funtion, this fuction will get the client's request and response"""
        
        clientRequestStr = self.socket.recv(1024)
        logging.getLogger('ThreadingHTTPServer').info("clientRequestStr is:\n" + clientRequestStr)

        #change to http status 200/ others 
        self.socket.send("""HTTP/1.1 200 OK
Content-Type: text/html

<html><body>Hello World</body></html>
""")
        logging.getLogger('ThreadingHTTPServer').info("Client disconnected..., killing thread for" +self.ip+":"+str(self.port))
        self.socket.close()

def initLogger():
    """Create a logger and log file named with today's day + connectionLog.txt """
    
    today = date.today()
    logging.basicConfig(filename=(today.strftime("%d%m%y")+"connectionLog.txt"),
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)
    logging.getLogger('ThreadingHTTPServer').info("The logger is initialized")

def run(port=12000):
    """Accept the port parameter (default is 12000) and start to listen to HTTP/TCP connections from client with corresponding port number.
        When new connection received from client, it will create a new thread from class clientThread to handle it"""
    
    try:
        initLogger()
        serverPort = port
        serverSocket = socket(AF_INET, SOCK_STREAM)
        # serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(("", serverPort)) #blind to local IP 
        threads = []

        while True:
            serverSocket.listen(5)
            logging.getLogger('ThreadingHTTPServer').info("Listening for incoming connections...")
            (clientsock, (clientIP, clientPort)) = serverSocket.accept()
            newthread = clientThread(clientIP, clientPort, clientsock)
            newthread.start()
            threads.append(newthread)

        for t in threads:
            t.join()

        logging.getLogger('ThreadingHTTPServer').info('Stopping ...\n')

    except socket.error as e:
            logging.getLogger('ThreadingHTTPServer').info(e)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    """Main function of the program, if running in terimal, it could take one argument as server's port number"""
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()