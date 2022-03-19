# https://www.tutorialspoint.com/python/python_multithreading.htm
# https://stackoverflow.com/questions/17453212/multi-threaded-tcp-server-in-python
from socket import *
from datetime import date, datetime
import threading, logging, os

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
        
        clientRequestStr = self.socket.recv(1024).decode()
        logging.getLogger('ThreadingHTTPServer').info("clientRequestStr is:\n" + clientRequestStr)

        headers = clientRequestStr.split("\n")
        fields = headers[0].split(" ")
        requestType = fields[0]
        requestedFileName = fields[1]

        isBadReq = False
        if requestType != "GET" or "favicon.ico" == requestedFileName or "" == requestedFileName:
            isBadReq == True
        logging.getLogger('ThreadingHTTPServer').info("clientRequest file is: " + requestedFileName)

        if isBadReq == True:
            # Bad Request
            response = "HTTP/1.1 400 Bad Request\n\n<html><body><h1>400 Bad Request</h1></body></html>"
            self.socket.send(response.encode())
            self.socket.close()
        else:
            # file found
            if requestedFileName == "/":
                requestedFileName = "/index.html"

            if os.path.isfile('.' + requestedFileName):

                # Get the last modified time, 
                lastModifiedTime = os.path.getmtime('./' + requestedFileName)
                lastModifiedTimeStr = datetime.fromtimestamp(lastModifiedTime).strftime('%a, %d %b %Y %H:%M:%S GMT')
                logging.getLogger('ThreadingHTTPServer').info("lastModifiedTime is: " + lastModifiedTimeStr)
                lastModifiedTimeHeadStr = "Last-Modified: " + lastModifiedTimeStr

                # Get the file length
                contentLength = os.path.getsize('./' + requestedFileName)
                contentLengthStr = "Content-Length: " + str(contentLength)

                # Get the file type
                imageFileType = ["jpg","png","gif"]
                # textFileType = ["txt",]
                fileType = requestedFileName.split(".")[-1]
                fileTypeStr = "Content-Type: text/html"
                if fileType in imageFileType:
                    fileTypeStr = "Content-Type: image/" + fileType
                    logging.getLogger('ThreadingHTTPServer').info(fileTypeStr)

                headerStr = ""
                contentStr = ""
                if fileTypeStr == "Content-Type: text/html":
                    f = open('.' + requestedFileName)
                    headerStr = """HTTP/1.1 200 OK\r\n""" + \
                                lastModifiedTimeHeadStr + """\r\n""" + \
                                contentLengthStr + """\r\n""" + \
                                fileTypeStr + """\r\n\r\n"""  
                    contentStr = f.read() 
                    f.close()

                    self.socket.send(headerStr.encode())
                    self.socket.send(contentStr.encode())
                else:
                    f = open('.' + requestedFileName, "rb") # read image in binary 
                    headerStr = """HTTP/1.1 200 OK\r\n""" + \
                                lastModifiedTimeHeadStr + """\r\n""" + \
                                """Accept-Ranges: bytes\r\n""" + \
                                contentLengthStr + """\r\n""" + \
                                fileTypeStr + """\r\n\r\n"""     
                    contentStr = f.read()
                    f.close()

                    self.socket.send(headerStr.encode())
                    self.socket.send(contentStr)
                logging.getLogger('ThreadingHTTPServer').info("headerStr:" + headerStr)
                
                # Example
                # HTTP/1.1 200 OK\r\n
                # Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n
                # Server: Apache/2.0.52 (CentOS)\r\n
                # Last-Modified: Tue, 30 Oct 2007 17:00:02 GMT\r\n
                # ETag: "17dc6-a5c-bf716880"\r\n
                # Accept-Ranges: bytes\r\n
                # Content-Length: 2652\r\n
                # Keep-Alive: timeout=10, max=100\r\n
                # Connection: Keep-Alive\r\n
                # Content-Type: text/html;

                # headers = {"If-Modified-Since ": timestamp}

                self.socket.close()
            else:
                # File not found
                response = "HTTP/1.1 404 Not Found\n\n<html><body><h1>404 File Not Found</h1></body></html>"
                self.socket.send(response.encode())
                self.socket.close()

        logging.getLogger('ThreadingHTTPServer').info("Disconnected to client ..., killing thread for: " +self.ip+":"+str(self.port)) 
        return 

def initLogger():
    """Create a logger and log file named with today's day + connectionLog.txt """
    
    today = date.today()
    logging.basicConfig(filename=(today.strftime("%d%m%y")+"connectionLog.txt"),
                                filemode='a',
                                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                datefmt='%H:%M:%S',
                                level=logging.DEBUG)
    logging.getLogger('ThreadingHTTPServer').info("The logger is initialized")

def run(port=80):
    """Accept the port parameter (default is 80 for HTTP) and start to listen to HTTP/TCP connections from client with corresponding port number.
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
        
        serverSocket.close()

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