from socket import *
serverName = '127.0.0.1'
serverPort = 80
serverPath = "/bookstore"
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

request = "POST /test/ HTTP/1.1\r\n\r\n"
#getRequest = "GET / HTTP/1.1\r\n" + serverName + ":"+ str(serverPort) + serverPath  + \
#            + "\r\n\r\n"
clientSocket.send(request.encode())
modifiedSentence = clientSocket.recv(1024)
print ('From Server (last):', modifiedSentence.decode())