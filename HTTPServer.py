from socket import *
from datetime import date, datetime
import threading, logging, os, time

class clientThread(threading.Thread):
    """This class is use to create a client thread for a HTTP connection"""

    def __init__(self, ip, port, socket):
        """Overriding the thread init funtion, added ip, port, socket parameter for this thread"""
        
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.live = True
        self.threadLiveTime = time.time() + 5 # default live time of the thread to listen connection is 5s
        logging.getLogger('ThreadingHTTPServer').info("[+] New thread started for "+ip+":"+str(port))

    def run(self):
        """Overriding the thread run funtion, this fuction will get the client's request and response"""
        
        while (self.live == True) and (time.time() < self.threadLiveTime):
            clientRequestStr = self.socket.recv(1024).decode()
            logging.getLogger('ThreadingHTTPServer').info("clientRequestStr is:\n" + clientRequestStr)

            headers = clientRequestStr.split("\n")
            fields = headers[0].split(" ")
            requestType = fields[0]
            requestedFileName = fields[1]

            requestTypeNumber = 200
            if requestType != "GET"  or requestType != "HEAD" or "favicon.ico" == requestedFileName:
                requestTypeNumber == 400
            
            if requestTypeNumber == 400:
                # Bad Request
                response = "HTTP/1.1 400 Bad Request\n\n<html><body><h1>400 Bad Request</h1></body></html>"
                self.socket.send(response.encode())
                logging.getLogger('ThreadingHTTPServer').info(response)
                self.live = False
            else:
                if requestedFileName == "/":
                    requestedFileName = "/index.html"

                # file found
                if os.path.isfile('.' + requestedFileName):

                    connectionStr, keepAliveTimeStr, keepAliveTime = self.getRequestedConnectionStatus(clientRequestStr)
                    lastModifiedTimeStr, contentLengthStr = self.getLocalFileStatus(requestedFileName)
                    
                    # compare the last modified time with brower file and local file 
                    findStr = "If-Modified-Since: "
                    clientLastModifiedTime = "0"
                    clientLastModifiedTimeStr = ""
                    isModified = True
                    urlStartPos = clientRequestStr.find(findStr)
                    if urlStartPos != -1:
                        urlEndPos = clientRequestStr.find("\r", urlStartPos)
                        if urlEndPos != -1:
                            clientLastModifiedTime = clientRequestStr[urlStartPos + len(findStr):urlEndPos]
                            clientLastModifiedTimeStr = "Last-Modified: " + clientLastModifiedTime

                    if clientLastModifiedTimeStr == lastModifiedTimeStr:
                        isModified = False

                    # Get the file type
                    imageFileType = ["jpg","png","gif"]
                    # textFileType = ["txt",]
                    fileType = requestedFileName.split(".")[-1]
                    fileTypeStr = "Content-Type: text/html"
                    if fileType in imageFileType:
                        fileTypeStr = "Content-Type: image/" + fileType

                    headerStr = ""
                    contentStr = ""
                    if isModified == True:
                        if fileTypeStr == "Content-Type: text/html":
                            f = open('.' + requestedFileName)
                            headerStr = """HTTP/1.1 200 OK\r\n""" + \
                                        "Server: Python 2.7\r\n" + \
                                        lastModifiedTimeStr + """\r\n""" + \
                                        contentLengthStr + """\r\n""" + \
                                        keepAliveTimeStr + """\r\n""" + \
                                        connectionStr + """\r\n""" + \
                                        fileTypeStr + """\r\n\r\n"""  
                            contentStr = f.read() 
                            f.close()

                            self.socket.send(headerStr.encode())
                            if requestType != "HEAD":
                                self.socket.send(contentStr.encode())
                        else:
                            f = open('.' + requestedFileName, "rb") # read image in binary 
                            headerStr = """HTTP/1.1 200 OK\r\n""" + \
                                        "Server: Python 2.7\r\n" + \
                                        lastModifiedTimeStr + """\r\n""" + \
                                        """Accept-Ranges: bytes\r\n""" + \
                                        contentLengthStr + """\r\n""" + \
                                        keepAliveTimeStr + """\r\n""" + \
                                        connectionStr + """\r\n""" + \
                                        fileTypeStr + """\r\n\r\n"""     
                            contentStr = f.read()
                            f.close()

                            self.socket.send(headerStr.encode())
                            if requestType != "HEAD":
                                self.socket.send(contentStr)
                    else:
                        headerStr = "HTTP/1.1 304 Not Modified\n\n"
                        self.socket.send(headerStr.encode())

                    logging.getLogger('ThreadingHTTPServer').info("Response headerStr is:\n" + headerStr)

                    if connectionStr == "Connection: Keep-Alive":
                        self.threadLiveTime = time.time() + float(keepAliveTime)
                    else:
                        self.live = False

                # file not found
                else:
                    response = "HTTP/1.1 404 Not Found\n\n<html><body><h1>404 File Not Found</h1></body></html>"
                    self.socket.send(response.encode())
                    logging.getLogger('ThreadingHTTPServer').info(response)
                    self.live = False

        self.socket.close()
        logging.getLogger('ThreadingHTTPServer').info("Disconnected to client ..., killing thread for: " +self.ip+":"+str(self.port)) 
        return 

    def getRequestedConnectionStatus(self, requestStr):
        """ Get the client requested connection status and return a str as connection staus and a time to indicate the alive time"""

        findStr = "Connection: "
        requestedConnection = "Connection: close" 
        connectionStr = "Connection: Keep-Alive" # default connection is Keep-Alive if not specified by client
        urlStartPos = requestStr.find(findStr)
        if urlStartPos != -1:
            urlEndPos = requestStr.find("\r", urlStartPos)
            if urlEndPos != -1:
                requestedConnection = requestStr[urlStartPos + len(findStr):urlEndPos]
        if requestedConnection.lower() != "keep-alive":
            connectionStr = "Connection: close"

        findStr = "Keep-Alive: "
        keepAliveTime = "5" # default keep alive time is 5sec if not specified by client
        keepAliveTimeStr = ""
        urlStartPos = requestStr.find(findStr)
        if urlStartPos != -1:
            urlEndPos = requestStr.find("\r", urlStartPos)
            if urlEndPos != -1:
                keepAliveTime = requestStr[urlStartPos + len(findStr):urlEndPos]
        if int(keepAliveTime) != 0:
            keepAliveTimeStr = "Keep-Alive: timeout=" + keepAliveTime + ", max=100"
        return connectionStr, keepAliveTimeStr, keepAliveTime

    def getLocalFileStatus(self, requestedFileName):
        """ Get the requested file status and return the last modify time and file length"""
        # Get the last modified time of the requested file 
        lastModifiedTime = os.path.getmtime('./' + requestedFileName)
        lastModifiedTimeStr = "Last-Modified: " + datetime.fromtimestamp(lastModifiedTime).strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Get the file length
        contentLength = os.path.getsize('./' + requestedFileName)
        contentLengthStr = "Content-Length: " + str(contentLength)
        return lastModifiedTimeStr, contentLengthStr

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