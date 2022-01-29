import json
import subprocess

def getNetwork(ip, mask):
    maskTab = [ int(x) for x in mask.split(".") ]
    ipTab = [ int(x) for x in ip.split(".") ]
    networkIpTab = [ str(maskTab[i] & ipTab[i]) for i in range(0,4)]
    networkMaskTab = [ str(255 - maskTab[i]) for i in range(0,4)]

    return [".".join(networkIpTab), ".".join(networkMaskTab)]

def getTopology(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def getConfigFile(hostname, directory):
    command = "grep -iRl \"^hostname "+hostname+"\" "+ directory+ " | grep .cfg"
    return str(subprocess.check_output(['bash','-c', command])).split("'")[1][:-2]


