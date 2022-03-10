from socket import *
serverName = '127.0.0.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
print ('From Server:', modifiedSentence.decode())

while True:
    modifiedSentence = clientSocket.recv(1024)
    if "bye" in modifiedSentence.decode():
        print ('From Server (last):', modifiedSentence.decode())
        clientSocket.close()
        break
    else:
        print ('From Server:', modifiedSentence.decode())
