import socketserver
import json
import socket
import logging.config
import sys

# Get running IP
HOST = socket.gethostbyname(socket.gethostname())

# list of all servers
serverList = []

# global list of all the locked file
global lockedFileslist
lockedFileslist = []

# Main Logger
logging.basicConfig(filename='mainServer.log', level=logging.DEBUG, filemode='w',
                    format='%(asctime)s\tLogger: %(name)s\tLevel: %(levelname)s\tEvent: %(message)s',
                    datefmt='%Y:%m:%d %H:%M:%S')

# Set Logging Configurations
serverLog = logging.getLogger("Main Server")
loggingHandler = logging.StreamHandler(stream=sys.stdout)
serverLog.addHandler(loggingHandler)
serverLog.setLevel(logging.DEBUG)


# Handler for the user class
class UserHandler(socketserver.BaseRequestHandler):

    # initial handler
    def handle(self):

        # gets initial handle request
        self.data = self.request.recv(1024).strip()

        # log request
        log_event = "[+] CLIENT: " + str(self.client_address[0]) + ":" + str(self.client_address[1]) + " REQUEST: " + str(self.data.decode())
        serverLog.info(log_event)

        #################################################################################
        # statements below filter the request
        #################################################################################

        # a new server joins main
        if "serverip" in format(self.data):
            ipadd = self.data.decode("utf-8").split(":")[1]
            if ipadd not in serverList:
                serverList.append(self.data.decode("utf-8").split(":")[1])
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))

            log_event = "Server " + str(len(serverList)) + " has stared on " + self.data.decode("utf-8").split(":")[1] + ":50000"
            serverLog.info(log_event)

        # a server requests all of main's IPs
        if "getip" in format(self.data):
            self.request.sendall(bytes(';'.join(serverList) , "utf-8"))

            log_event = "[+] Active server list returned to: " + str(self.client_address[0])
            serverLog.info(log_event)

        # returns locked files
        if "getlockedfiles" in format(self.data):
            global lockedFileslist
            self.request.sendall(bytes(';'.join(lockedFileslist), "utf-8"))

        # returns userdata
        if "userdata" in format(self.data):

            file = open("configuration files/userConfig.txt", mode='r')
            lines = file.readlines()
            data = ""

            # for all the USERS, send what is in i the userConfig.txt file
            for line in lines:
                if data != "":
                    data = data + ";" + line
                else:
                    data = data + line
            self.request.sendall(bytes(str(data) + "\n" , "utf-8"))

        # locks a file
        if "lockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            if filename not in lockedFileslist:
                lockedFileslist.append(filename)

            log_event = "[*] " + self.data, "has been locked"
            serverLog.info(log_event)

        # unlocks a file
        if "unlockfile" in format(self.data):
            filename = self.data.decode("utf-8").split(":")[1]
            while(filename in lockedFileslist):
                lockedFileslist.remove(filename)

            log_event = "[*] " + self.data, "has been unlocked"
            serverLog.info(log_event)

        # gets permission in the json file
        if "getPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            # sends the requested information
            if data['filename'] in filedata:
                result = filedata[data['filename']]
            print(result)
            jsData = json.dumps(result)

            self.request.sendall(bytes(jsData, "utf-8"))

        # insert new permissions in the json file
        if "insertPermissions" in format(self.data):
            print(json.loads(self.data))
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            # ?????????
            if data['fileDetails']['name'] in filedata:
                print("temp")
                print(filedata[data['fileDetails']['name']]['users'])
                temp = filedata[data['fileDetails']['name']]['users']
                temp[data['fileDetails']['users']['name']] = data['fileDetails']['users']['per']
                filedata[data['fileDetails']['name']] = {"name" : data['fileDetails']['name'], "owner": filedata[data['fileDetails']['name']]['owner'], "users":  temp}

            # ????????????
            else:
                filedata[data['fileDetails']['name']] =  {"name" : data['fileDetails']['name'], "owner": data['fileDetails']['owner'], "users":  {}}

            # ???????????
            with open("configuration files/permissions.json", "w") as file1:
                json.dump(filedata, file1)

            # ???????????
            self.request.sendall(bytes(str("200"), "utf-8"))

        # deletes a given permission in the json file
        if "delPermissions" in format(self.data):
            data = json.loads(self.data)
            file = open("configuration files/permissions.json")
            filedata = json.load(file)

            # ?????????????
            if data['filename'] in filedata:
                del filedata[data['filename']]

            with open("configuration files/permissions.json", "w") as file1:
                json.dump(filedata, file1)

            # ????????????????
            self.request.sendall(bytes(str("200"), "utf-8"))


if __name__ == "__main__":

    # Start Server
    with socketserver.TCPServer((HOST, 0), UserHandler) as server:

        # get IP and PORT
        ip, port = server.server_address

        # Display IP and Port
        log_event ="[+] Main Server Started on IP:" + ip +" and PORT: ", port
        serverLog.info(log_event)

        # Serve forever
        server.serve_forever()