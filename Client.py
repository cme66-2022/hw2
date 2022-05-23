import time
from socket import *
import sys
import os
import logging



class client:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.buffer = 4096
        self.csocket = None
        self.dsocket = None
        self.log = logging.getLogger()

#The connect method is meant to be used to create a control socket connection
    def connect(self):
#The below lines of code are creating the control socket and logging the messages that were sent and received betweem the client and server
        self.csocket = socket(AF_INET, SOCK_STREAM)
        self.csocket.connect((self.hostname, self.port))
        self.log.info("The client has sent a request to connect to the server")
        return self.getStatus(self.receive())

#The send method is used to send messages from the client to the server
    def send(self,message):
#The codes below are used to send a message through the control socket to the server and also to log the request sent. The point is that all commands sent to the server should be logged within the logger file.
        self.csocket.send(message.encode())
        self.log.info("The client has sent the following message to the server. \'{}\'".format(message))

#The dsend method sends information through a data socket
    def dsend(self,message):
#This code encodes the message into bytes and sends it through the data socket that is established by using either pasv or epsv
        self.dsocket.send(message.encode())
        self.log.info("The client has sent the following message to the server on the data socket. \'{}\'".format(message))


#This method is used to receive messages, clear the buffer, and print the message to the terminal
    def receive(self):
        message_bytes = b''
        self.csocket.settimeout(1)
        while True:
            try:
                received = self.csocket.recv(self.buffer)
            except timeout:
                break
            message_bytes += received
            if len(received) == 0:
                break
        self.log.info("The server sent the following response. \'{}\'".format(message_bytes.decode()))
        print(message_bytes.decode())
        #print(msg_received)
        return message_bytes

#The dreceive method receives data from data socket as well as clears the buffer and prints that data sent through the socket to the terminal
    def dreceive(self):
        message_bytes = b''
        self.dsocket.settimeout(1)
        while True:
            try:
                received = self.dsocket.recv(self.buffer)

            except timeout:
                break

            message_bytes += received
            if len(received) == 0:
                break
        #print(msg_received)
        self.log.info("The server sent the following response on the data socket.\n \'{}\'".format(message_bytes.decode()))
        #print(message_bytes.decode())
        return message_bytes

#The user method allows a user to login in if they give the proper credentials
    def user(self,username):
        self.send("USER {}\r\n".format(username))
        return self.getStatus(self.receive())

#The password method is used to input a password to log into the system
    def password(self,password):
        self.send("PASS {}\r\n".format(password))
        return self.getStatus(self.receive())

#This method is used to close the socket and close out of the program
    #Finished
    def quit(self):
        self.send("QUIT\r\n")
        self.receive()
        self.csocket.close()

#The method pwd prints the current working directory
    #Finished
    def pwd(self):
        self.send("PWD\r\n")
        self.receive()

#This method is used to establish a data socket
    #Finished
    def pasv(self):
        self.send("PASV\r\n")
        returned = self.receive().decode()
# Below I am parsing out the hostname and IP address so that I can establish the data socket
        socketData = returned.split("(")[1].split(")")[0]
        dataArray = socketData.split(",")
        hostname = "{}.{}.{}.{}".format(dataArray[0],dataArray[1],dataArray[2],dataArray[3])
        port = (int(dataArray[4]) * 256) + int(dataArray[5])
#Below is where the data socket is created
        self.dsocket = socket(AF_INET, SOCK_STREAM)
        self.dsocket.connect((hostname,port))
        return self.getStatus(self.receive())

# This method is used to establish a data socket
    def epsv(self):
        self.send("EPSV \r\n")
#The dataArray takes in the values for the port number used to establish a data socket.
#The element in the array that corresponds with the port number is then stored in the variable port
        dataArray = self.receive().decode().split("|")
        port = int(dataArray[3])
        self.dsocket = socket(AF_INET,SOCK_STREAM)
        self.dsocket.connect((self.hostname,port))
        return self.getStatus(self.receive())

# The eprt method is used to establish an extended port data socket
#This method is not completed yet
    def eprt(self):
        self.send("EPRT |{}|{}|{}|\r\n".format(str(1),self.hostname,str(self.port)))
        self.receive()

#The cwd method changes the current working directory to the directory that is given in the parameter, path
    #Finished
    def cwd(self, path):
        self.send("CWD {}\r\n".format(path))
        return self.getStatus(self.receive())

#The list method is used to list all the files in the file path that is given
    def list(self, path):
        try:
            self.send("LIST {}\r\n".format(path))
            self.receive()
#using dreceive we are able to receive all the necessary data that is sent through the data socket
            print(self.dreceive().decode())
            self.dsocket.close()
        except:
            return self.getStatus(self.receive())

#The syst method is used to report the type of operating system being used at the server
    def syst(self):
        self.send("SYST\r\n")
        return self.getStatus(self.receive())

#The help method is used to get more information on some  commands that are used or to list all the available commands
    def help(self):
        self.send("HELP \r\n")
        return self.getStatus(self.receive())
        #Don't know if dreceive is necessary in help. Also, I am not sure why when help is called with a specific command it does not give more info on the command specified
        #self.dreceive()

#The store method is used to send data through the data connection for it to be stored as a file in the specified path
    def store(self,path):
        self.send("STOR {}\r\n".format(path))
        self.receive()
        #A file is opened in read mode to get the text from the file
        file = open(path, "r")
        text = file.read()
        #Files must always be closed after being used
        file.close()
        #The data from the file is sent in the data socket
        self.dsend(text)
        #The data socket must be closed after it is used
        self.dsocket.close()
        return self.getStatus(self.receive())

#The retrieve method is used to retrieve a copy of a file that is in the server's filesystem
    def retrieve(self,path):
        self.send("RETR {}\r\n".format(path))
        self.receive()
        #The text from the server file is stored in the variable file_text
        file_text = self.dreceive().decode()
        self.dsocket.close()
        #The file that was pulled from the server has a copy created on the client side
        #ThisIsTaysFile.txt is an example of this happening
        file = open(path, "w")
        file.write(file_text)
        file.close()

#The method getStatus is used to get the status code to be used for error handling
    def getStatus(self,message):
        code = message.decode().split(" ")[0]
        return code





#The main function below is where the logging file will be created and the user interface and the majority of the error handling will take place.
def main():
#The below code creates a logging file that will log all the commands sent to the server and responses received from the server as well
    format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename="mylog.log", filemode="a",format=format, level=logging.INFO)

#An instance of the class client is created below using the hardcoded values given from the assignment

    try:
        c = client('10.246.251.93', 21)
        handling = c.connect()
        if handling == "220":
            ans = input("Please enter your username.\n")
            handling = c.user(ans)
            ans = input("Please enter your password.\n")
            handling = c.password(ans)
            if handling == "230":
                while True:
                    ans = input("Please enter the number of the command you would like to perform.\n1.Change Working Directory\n2.Print Working Directory\n3.Display Operating System Version\n4.List Directory Files\n5.Help\n6.Retrieve File\n7.Send File\n8.Quit\n")
                    ans = ans.upper()
                    if(ans == "1"):
                        ans = input("Enter the file path for the directory you would like to change to.\n (For example, to change to the parent directory of your current working directory you can type \'..\')\n")
                        handling = c.cwd(ans)
                        if handling == "550":
                            c.log.info("The user interface has printed the following message:\'The path mentioned does not exist.\'")
                            print("The path mentioned does not exist.\n")
                        elif handling == "421":
                            break
                    elif(ans == "8"):
                        handling = c.quit()
                        if handling == "421":
                            break
                        break
                    elif(ans == "2"):
                        handling = c.pwd()
                        if handling == "421":
                            pass
                    elif (ans == "3"):
                        handling = c.syst()
                        if handling == "421":
                            break
                    elif (ans == "4"):
                        ans = input("Enter the file path for the directory you would like to list.\n(For example, to list all of the files in the current working directory you can enter \'.\')\n")
                        c.pasv()
                        handling = c.list(ans)
                        if handling == "421":
                            break
                    elif (ans == "5"):
                        handling = c.help()
                        if handling == "421":
                            break
                    elif(ans == "6"):
                        ans = input("Enter the full file path for the file you would like to retrieve.\n")
                        c.epsv()
                        c.retrieve(ans)

                    elif(ans == "7"):
                        ans = input("Enter the full file path for the file you would like to store to the server.\n")
                        c.pasv()
                        handling = c.store(ans)
                        if handling == "226":
                            c.log.info("The user interface has printed the following message:\'The file is stored.\'")
                            print("The file is stored.\n")
                        else:
                            c.log.info("The user interface has printed the following message:\'The file path given does not exist.\'")
                            print("The file path given does not exist.\n")
                    else:
                        c.log.info("The user interface printed the following message: \'That command is not recognized\'")
                        print("\nThat command is not recognized\n")
            else:
                c.log.info("The user interface printed the following message: \'The username or password provided was incorrect.\nExiting...\'")
                print("The username or password provided was incorrect.\nExiting...")

        else:
            c.log.info("The user interface printed the following message:\'The hostname or port number of your client is incorrect.\n Exiting....\'")
            print("The hostname or port number of your client is incorrect.\n Exiting....")
    except:
        pass





if __name__ == "__main__":
    main()