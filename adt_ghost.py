import os
import gzip
import json


class File():
    def __init__(self, name, path, fullFile, fileType, content):
        self.name = name 
        self.path = path
        self.fullFile = fullFile
        self.fileType = fileType
        self.content = content
        

class Directory(): 
    def __init__(self):
        self.fileList = []
        self.initializeFiles()
        
        
    def initializeFiles(self):
        currDir = os.getcwd()
        fileList = os.listdir(currDir) 
        for file in fileList:
            name = file
            path = os.getcwd()
            fullFile = path + "/" + name
            if ".gz" in name:
                fileType = "gz"
                with gzip.open(fullFile,'rt', encoding="ISO-8859-1") as f:
                    try:
                        readLines = f.readlines()
                    except UnicodeDecodeError:
                        print("Error with encoding for file", name)
                        break
                f.close()
            elif name[0] == ".":
                pass
            else:
                fileType = "log"
                with open(fullFile, 'r', encoding="ISO-8859-1") as f:
                    try:
                        readLines = f.readlines()
                    except UnicodeDecodeError:
                        print("Error with encoding for file: ", name)
                        break
                f.close()
            content = readLines
            # print(content)
            newFile = File(name, path, fullFile, fileType, content)
            self.fileList.append(newFile)
            
            
class Device():
    def __init__(self, nssId, zoneId):
        self.nssId = nssId
        self.zoneId = zoneId
    
    
    def getProdId(self, directory):
        for file in directory:
            if "gc3-api" in file.name:
                for line in file.content:
                    if (self.nssId) in line and 'zoneStatusChange' in line:
                        print("node line", line)
                        eventData = line[line.find("event data = ") + len("event data = "):]
                        jsonLine = json.loads(eventData)
                        print(jsonLine)
                        for item in jsonLine:
                            self.prodId = (item['device']['productId'])


def getGhostDevices(directory):
    nodeList=[]
    for file in directory:
        if "hubCoreLog" in file.name:
            for line in file.content:
                if "Failed to lookup" in line and "NSS" in line:
                    print(line)
                    nodeId = line[line.find("NSS"):].split("|")[1]
                    print(line, nodeId, file.name)
                    nodeList.append(nodeId.strip())
    nodeSet = set(nodeList)
    if len(nodeSet) < 1:
    	print("No Ghost Devices Found")
    return nodeSet



def getNSS(directory, nodeList):
    nssDict={}
    for node in nodeList:
        for file in directory:
            if "hubCoreLog" in file.name:
                for line in file.content:
                    if "Zone Status Change" in line and "NSS|" + str(node) in line:
                        nssIdStart = line.find("NSS|")
                        nssIdEnd = line.find(",",nssIdStart)
                        nssId = line[nssIdStart:nssIdEnd]
                        zoneStart = line.find("zone:")
                        zoneEnd = line.find(",", zoneStart)
                        zone = (line[zoneStart:zoneEnd]).split(":")[1].strip()
                        nssDict[nssId] = zone
    return nssDict

                

def main():
    thisDirectory = Directory()
    directoryFiles = thisDirectory.fileList
    deviceList = []
    nodes = getGhostDevices(directoryFiles)
    nssList = getNSS(directoryFiles, nodes);

    for nss in nssList:
        newDevice = Device(nss, nssList[nss])
        newDevice.getProdId(directoryFiles)
        deviceList.append(newDevice)


    print("\n")
    print("################")
    print("\n")


    for device in deviceList:
        print("NSS: " , device.nssId)
        print("Zone:", device.zoneId)
        print("Product Id: ", device.prodId)
        print("\n")


if __name__ == "__main__":
	main()
	        
