import json
import re
import subprocess

def defineHeader(hostname):
    Header = "!\n"*9 + "version 15.2\n" + "service timestamps debug datetime msec\n" + "service timestamps log datetime msec\n" + "!\n" + "hostname "+ hostname +"\n" + "!\n" + "boot-start-marker\n" +"boot-end-marker\n" + "!\n"*3 + "no aaa new-model\n" + "no ip icmp rate-limit unreachable\n" + "ip cef\n" + "!\n"*6 +"no ip domain lookup\n"+ "no ipv6 cef\n"+ "!\n"*2 +"mpls label protocol ldp \nmultilink bundle-name authenticated\n" +"!\n"*9 +"ip tcp synwait-time 5\n" + "!\n"*12
    return Header

def defineFooter():
    Fin = "\n" + "ip forward-protocol nd\n"+"!\n"*2 +"no ip http server\n"+"no ip http secure-server\n"+"!\n"*4 +"control-plane\n"+"!\n"*2+"line con 0\n"+" exec-timeout 0 0\n"+" privilege level 15\n" + " logging synchronous\n" + " stopbits 1 \n" +"line aux 0\n" +" exec-timeout 0 0\n" +" privilege level 15\n" + " logging synchronous\n"+" stopbits 1\n"+"line vty 0 4\n"+" login\n" + "!\n" *2 +"end"
    return Fin

def defineInterfaceConfig(interface):
    ipConfig = ""
    if ( interface["config"] == 'no' ):
        if (re.search("^Gigabit*", interface["name"] )):
            ipConfig = "interface " + interface["name"] +" \n no ip address\n shutdown\n negotiation auto\n!"
        else:
            ipConfig = "interface " + interface["name"] +" \n no ip address\n shutdown\n duplex full\n!"
    elif (re.search("^Loopback*", interface["name"] )): 
        ipConfig = "interface "+ interface["name"] + "\n ip address " + interface["ip"] + " "+ interface["mask"] + "\n!"
    else: 
        ipConfig = "interface "+ interface["name"] + "\n ip address " + interface["ip"] + " " + interface["mask"] + "\n"+" negotiation auto\n mpls ip\n!"


    return ipConfig

def getNetwork(ip, mask):
    maskTab = [ int(x) for x in mask.split(".") ]
    ipTab = [ int(x) for x in ip.split(".") ]
    networkIpTab = [ str(maskTab[i] & ipTab[i]) for i in range(0,4)]
    networkMaskTab = [ str(255 - maskTab[i]) for i in range(0,4)]

    return [".".join(networkIpTab), ".".join(networkMaskTab)]


def defineOSPFConfig(router): 
    ospfConfig = ""
    #router-ospf = router[router-id].split(".")[3]
    ospfConfig = "router ospf "+ router["router-id"].split(".")[0] + " \n"+ \
    " router-id " + router["router-id"]+" \n"

    for int in router["interfaces"] : 
        if(int["config"] == "yes"):
            networkInfo = getNetwork(int["ip"], int["mask"])
            ospfConfig = ospfConfig + " network " +networkInfo[0]+" "+ networkInfo[1] +" area 0\n"
    
    ospfConfig = ospfConfig + "! \n"

    return ospfConfig

def defineCoreRouterConfig(router):
    config = defineHeader(router["name"])
    for int in router["interfaces"]:
        config = config + defineInterfaceConfig(int) + "\n"
    config = config + defineOSPFConfig(router)
    config = config + defineFooter()

    return config

def defineEdgeRouterConfig(router):
    config = defineHeader(router["name"])
    for int in router["interfaces"]:
        config = config + defineInterfaceConfig(int) + "\n"
    config = config + defineOSPFConfig(router)
    config = config + defineFooter()

    return config

def getTopology(file):
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

def getConfigFile(hostname):
    command = "grep -iRl \"^hostname "+hostname+"\" /home/abdel/GNS3/projects/test_script/project-files/dynamips/ | grep .cfg"
    return str(subprocess.check_output(['bash','-c', command])).split("'")[1][:-2]


def createCfgFile(name, config):
    with open(name, 'w') as f:
        f.write(config)

def deployTopology(topology):
    
    for edge in topology["PE"]:
        confFile = getConfigFile(edge["name"])
        createCfgFile(confFile, defineEdgeRouterConfig(edge))
        #print(confFile)
    for core in topology["Core"]:
        confFile = getConfigFile(core["name"])
        createCfgFile(confFile, defineCoreRouterConfig(core))
        #print(confFile)


def main() :
    data = getTopology('data.json')
    deployTopology(data)
    
    #createCfgFile(getConfigFile("R1"), 'test2 \nhostname R1')


if __name__ == "__main__" : 
    main()