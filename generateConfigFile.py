import json
import re
import subprocess
import utils
import cfg

def defineHeader(hostname):
    Header = "!\n"*9 + "version 15.2\n" + "service timestamps debug datetime msec\n" + "service timestamps log datetime msec\n" + "!\n" + "hostname "+ hostname +"\n" + "!\n" + "boot-start-marker\n" +"boot-end-marker\n" + "!\n"*3 + "no aaa new-model\n" + "no ip icmp rate-limit unreachable\n" + "ip cef\n" + "!\n"*6 +"no ip domain lookup\n"+ "no ipv6 cef\n"+ "!\n"*2 +"mpls label protocol ldp \nmultilink bundle-name authenticated\n" +"!\n"*9 +"ip tcp synwait-time 5\n" + "!\n"*12
    return Header

def defineFooter():
    Fin = "ip forward-protocol nd\n"+"!\n"*2 +"no ip http server\n"+"no ip http secure-server\n"+"!\n"*4 +"control-plane\n"+"!\n"*2+"line con 0\n"+" exec-timeout 0 0\n"+" privilege level 15\n" + " logging synchronous\n" + " stopbits 1 \n" +"line aux 0\n" +" exec-timeout 0 0\n" +" privilege level 15\n" + " logging synchronous\n"+" stopbits 1\n"+"line vty 0 4\n"+" login\n" + "!\n" *2 +"end"
    return Fin


def defineInterfaceConfig(interface, isMpls):
    ipConfig = ""
    if ( interface["config"] == 'no' ):
        if (re.search("^Gigabit*", interface["name"] )):
            ipConfig = "interface " + interface["name"] +" \n no ip address\n shutdown\n negotiation auto\n!"
        else:
            ipConfig = "interface " + interface["name"] +" \n no ip address\n shutdown\n duplex full\n!"
    elif (re.search("^Loopback*", interface["name"] )): 
        ipConfig = "interface "+ interface["name"] + "\n ip address " + interface["ip"] + " "+ interface["mask"] + "\n!"
    elif not isMpls: 
        ipConfig = "interface "+ interface["name"] + "\n ip address " + interface["ip"] + " " + interface["mask"] + "\n"+" negotiation auto\n!"
    else:
        ipConfig = "interface "+ interface["name"] + "\n ip address " + interface["ip"] + " " + interface["mask"] + "\n"+" negotiation auto\n mpls ip\n!"
    return ipConfig

def defineOSPFConfig(router, AS):
    ospfPassive = ""
    ospfNetwork = ""
    ospfConfig = ""
    for int in router["interfaces"] : 
        if(int["config"] == "yes"):
            if router["as"] == AS:
                ospfConfig = "router ospf "+ router["router-id"].split(".")[0] + " \n"+ \
                " router-id " + router["router-id"]+" \n"
                
                if(int["link"] != "transit-ip" and int["link"] != ""):
                    ospfPassive = ospfPassive + " passive-interface "+ int["name"] + "\n"

                networkInfo = utils.getNetwork(int["ip"], int["mask"])
                ospfNetwork = ospfNetwork + " network " +networkInfo[0]+" "+ networkInfo[1] +" area 0\n"
    if ospfPassive != "":
        return ospfConfig + ospfPassive + ospfNetwork + "!\n"
    else:
        return ospfConfig + ospfNetwork + "!\n"


"""def defineBGPConfig(router):
    BgpConfig = ""
    return BgpConfig
"""

def defineBgpNeighbor(topology, router, AS):
    neighbors = getBGPNeighbor(topology, router)
    bgpNeighbor = "router bgp "+ str(router["as"])+"\n bgp router-id "+router["router-id"]+"\n bgp log-neighbor-changes \n"
    for neighbor in neighbors:
        if(neighbor["as"] == router["as"]):
            bgpNeighbor = bgpNeighbor + " neighbor "+ neighbor["ip"] + " remote-as " + router["as"] + "\n neighbor "+ neighbor["ip"] + " update-source Loopback0 \n"
        else:
            bgpNeighbor = bgpNeighbor + " neighbor "+ neighbor["ip"] + " remote-as " + neighbor["as"] + "\n"
    #print(bgpNeighbor + defineBgpNetwork(router, AS) +"!\n")   
    return bgpNeighbor + defineBgpNetwork(router, AS) +"!\n"

def defineBgpNetwork(router,AS):
    bgpNetwork = ""
    if(router["as"] != AS):
        for int in router["interfaces"]:
            if (int["config"] == "yes" and int["link"] == "transit-ip"):
                bgpNetwork = bgpNetwork + " network " + utils.getNetwork(int["ip"],int["mask"])[0]+" mask " + int["mask"] + "\n"
    return bgpNetwork

def getBGPNeighbor(topology, router):
    neighborTab = []
    for interface in router["interfaces"]:
        if(interface["config"] == "yes" and interface["link"] != "transit-ip" and interface["link"] != ""):
            neighborTab.append({"ip": interface["voisin"]["ip"], "as" : interface["voisin"]["as"]})
    
    for r in topology["routers"]:
        if(r["name"] != router["name"]):
            if (int(r["as"]) == int(router["as"])):
                #print("tes")
                neighborTab.append({"ip": getInterface(r, "Loopback0")["ip"], "as" : router["as"]})
            
    
    return neighborTab

def getInterface(router, interface): 
    for int in router["interfaces"]:
        if(int["name"] == interface):
            return int
    return {}


def defineRouterConfig(topology,router):
    config = defineHeader(router["name"])
    for int in router["interfaces"]:
        config = config + defineInterfaceConfig(int, router["as"] == cfg.AS) + "\n"
    config = config + defineOSPFConfig(router, cfg.AS) + defineBgpNeighbor(topology, router, cfg.AS) + defineFooter()

    return config

def createCfgFile(name, config):
    with open(name, 'w') as f:
        f.write(config)

def deployTopology(topology, directory):
    
    for router in topology["routers"]:
        print(router["name"])
        confFile = utils.getConfigFile(router["name"], directory)
        createCfgFile(confFile, defineRouterConfig(topology,router))
