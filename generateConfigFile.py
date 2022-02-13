import json
import re
import subprocess
import utils
import cfg

def defineHeader(router):
    Header = "!\n"*9 + "version 15.2\n" + "service timestamps debug datetime msec\n" + "service timestamps log datetime msec\n" + "!\n" + "hostname "+ router["name"] +"\n" + "!\n" + "boot-start-marker\n" +"boot-end-marker\n" + "!\n"*3 + "no aaa new-model\n" + "no ip icmp rate-limit unreachable\n" + "ip cef\n" + defineVRFConfig(router)+"!\n"*6 +"no ip domain lookup\n"+ "no ipv6 cef\n"+ "!\n"*2 +"mpls label protocol ldp \nmultilink bundle-name authenticated\n" +"!\n"*9 +"ip tcp synwait-time 5\n" + "!\n"*12
    return Header

def defineFooter(router):
    Fin = "ip forward-protocol nd\n"+"!\n"*2 + generateRouteMapConfig(router)+"\n"+"!\n"*2 +"control-plane\n"+"!\n"*2+"line con 0\n"+" exec-timeout 0 0\n"+" privilege level 15\n" + " logging synchronous\n" + " stopbits 1 \n" +"line aux 0\n" +" exec-timeout 0 0\n" +" privilege level 15\n" + " logging synchronous\n"+" stopbits 1\n"+"line vty 0 4\n"+" login\n" + "!\n" *2 +"end"
    return Fin


def defineInterfaceConfig(interface, isMpls, isVpn):
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
    elif isVpn:
        ipConfig = "interface "+ interface["name"] + "\n ip vrf forwarding "+ interface["voisin"]["client_name"]+"\n ip address " + interface["ip"] + " " + interface["mask"] + "\n"+" negotiation auto\n mpls ip\n!"
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
    familyString = " address-family ipv4 \n"
    neighbors = getBGPNeighbor(topology, router)
    bgpNeighbor = "router bgp "+ str(router["as"])+"\n bgp router-id "+router["router-id"]+"\n bgp log-neighbor-changes \n"
    for neighbor in neighbors:
        if(neighbor["as"] == router["as"]):
            bgpNeighbor = bgpNeighbor + "  neighbor "+ neighbor["ip"] + " remote-as " + router["as"] + "\n  neighbor "+ neighbor["ip"] + " update-source Loopback0 \n"
            familyString = familyString + "  neighbor " + neighbor["ip"] + " send-community \n"
        else:
            bgpNeighbor = bgpNeighbor + "  neighbor "+ neighbor["ip"] + " remote-as " + neighbor["as"] + "\n"
            familyString = familyString + "  neighbor " + neighbor["ip"] + " send-community \n" 
    return bgpNeighbor + defineBgpNetwork(router, AS) +" !\n" + familyString + configureInterfaceRouteMap(router) +" exit-address-family \n"

def defineBgpNetwork(router,AS):
    bgpNetwork = ""
    if(router["as"] != AS):
        for int in router["interfaces"]:
            if (int["config"] == "yes" and int["link"] == "transit-ip"):
                bgpNetwork = bgpNetwork + " network " + utils.getNetwork(int["ip"],int["mask"])[0]+" mask " + int["mask"] + "\n"
    return bgpNetwork

def generateRouteMapConfig(router):
    bgpComunity = ""
    routeMap = ""
    prefixList = ""
    http = "no ip http server \nno ip http secure-server \n! \n! \n"
    if router["as"] == cfg.AS:
        for interface in router["interfaces"]:
            if(interface["link"] == "client" or interface["link"] == "client-vpn"):
                prefixList = "ip prefix-list Group1 seq 10 permit 0.0.0.0/0 le 32 \n! \n"
                bgpComunity = "ip bgp-community new-format \nip community-list 1 permit "+ cfg.CLIENT_COMUNITY + "\n! \n"
                routeMap = "route-map Client_1 permit 10 \n  match ip address prefix-list Group1 \n  set local-preference 150 \n  set community " + cfg.CLIENT_COMUNITY + "\n! \n"
            elif(interface["link"] == "peer"):
                prefixList = "ip prefix-list Group1 seq 10 permit 0.0.0.0/0 le 32 \n! \n"
                bgpComunity = "ip bgp-community new-format \nip community-list 1 permit "+ cfg.CLIENT_COMUNITY + "\n! \n"
                routeMap = "route-map Peer_in permit 10 \n  match ip address prefix-list Group1 \n  set local-preference 100 \n  set community " + cfg.PEER_COMUNITY + "\n! \n"
                routeMap = routeMap + "route-map Peer_out permit 10 \n match community 1 \n!"
            elif(interface["link"] == "provider"):
                prefixList = "ip prefix-list Group1 seq 10 permit 0.0.0.0/0 le 32 \n! \n"
                bgpComunity = "ip bgp-community new-format \nip community-list 1 permit "+ cfg.CLIENT_COMUNITY + "\n! \n"
                routeMap = "route-map Provider_in permit 10 \n  match ip address prefix-list Group1 \n  set local-preference 50 \n  set community " + cfg.PROVIDER_COMUNITY + "\n! \n"
                routeMap = routeMap + "route-map Provider_out permit 10 \n match community 1 \n! \n"
    return bgpComunity + http+ prefixList+ routeMap

def configureInterfaceRouteMap(router):
    routeMap = ""
    if router["as"] == cfg.AS:
        for interface in router["interfaces"]:
            if(interface["link"] == "client" or interface["link"] == "client-vpn"):
                routeMap = routeMap + "  neighbor "+ interface["voisin"]["ip"]+" route-map Client_1 in \n"
            elif(interface["link"] == "peer"):
                routeMap = routeMap + "  neighbor "+ interface["voisin"]["ip"] +" route-map Peer_in in \n"
                routeMap = routeMap + "  neighbor "+ interface["voisin"]["ip"]+" route-map Peer_out out \n"
            elif(interface["link"] == "provider"):
                routeMap = routeMap + "  neighbor "+ interface["voisin"]["ip"]+" route-map Provider_in in \n"
                routeMap = routeMap + "  neighbor "+ interface["voisin"]["ip"]+" route-map Provider_out out \n"
    return routeMap

def getBGPNeighbor(topology, router):
    neighborTab = []
    for interface in router["interfaces"]:
        if(interface["config"] == "yes" and interface["link"] != "transit-ip" and interface["link"] != ""):
            neighborTab.append({"ip": interface["voisin"]["ip"], "as" : interface["voisin"]["as"]})
    
    for r in topology["routers"]:
        if(r["name"] != router["name"]):
            if (int(r["as"]) == int(router["as"])):
                neighborTab.append({"ip": getInterface(r, "Loopback0")["ip"], "as" : router["as"]})
            
    
    return neighborTab


def getVpnClientPE(topology, client_name, a_router):
    # Retourne les addresse des loopback des PE auxquels sont connectés nos clients VPN
    PELoopback = []
    for router in topology["routers"]:
        if( router["as"] == cfg.AS and router["name"] != a_router["name"]):
            for interface in router["interfaces"]:
                if(interface["link"] == "client-vpn" and interface["voisin"]["client_name"] == client_name) and getInterface(router, "Loopback0")["ip"] not in PELoopback:
                    PELoopback.append(getInterface(router, "Loopback0")["ip"])
        

    return PELoopback

def defineVRFConfig(router):
    # retourne la config de creation de la vrf
    Vrf = ""
    if router["as"] == cfg.AS:
        for interface in router["interfaces"]:
            if(interface["link"]  == "client-vpn"):
                Vrf = Vrf + "ip vrf " + interface["voisin"]["client_name"] + "\n" + " rd " + cfg.AS + ":" + str(cfg.RD) + "\n" + " route-target export " + cfg.AS + ":" + interface["voisin"]["client_number"] + "\n" + " route-target import " + cfg.AS + ":" + interface["voisin"]["client_number"] + "\n!\n"
                cfg.RD = cfg.RD + 1
    return Vrf


def defineVpnV4(PE):
    vpnv4 = ""
    for ip in PE:
        vpnv4 = vpnv4 + "  neighbor " + ip +" activate\n" + "  neighbor "+ ip +" send-community extended \n"
    return vpnv4


def bgpVpnConfig(topology, router, AS):
    vrfConfig = ""
    vpnv4Config = ""
    PE = []
    for interface in router["interfaces"]:
        if(interface["link"] == "client-vpn"):
            vrfConfig = vrfConfig + " address-family ipv4 vrf " + interface["voisin"]["client_name"]+ "\n" + "  neighbor "+ interface["voisin"]["ip"] +" remote-as " +interface["voisin"]["as"] +" \n" + "  neighbor " + interface["voisin"]["ip"] + " activate \n" + \
                " exit-address-family \n !\n"
            for ip in getVpnClientPE(topology, interface["voisin"]["client_name"], router):
                if ip not in PE:
                    PE.append(ip)
    
    vpnv4Config = vpnv4Config + defineVpnV4(PE)
    
    if(vpnv4Config != ""):
        vpnv4Config = " address-family vpnv4 \n" + vpnv4Config + " exit-address-family\n !\n"
    return vpnv4Config + vrfConfig

def getInterface(router, interface): 
    for int in router["interfaces"]:
        if(int["name"] == interface):
            return int
    return {}

def defineBGPConfig(topology, router, AS):
    if( bgpVpnConfig(topology, router, AS) != ""):
        return defineBgpNeighbor(topology, router, AS) + " !\n" + bgpVpnConfig(topology, router, AS)
    return defineBgpNeighbor(topology, router, AS) + "!\n"

def defineRouterConfig(topology,router):
    config = defineHeader(router)
    for int in router["interfaces"]:
        config = config + defineInterfaceConfig(int, router["as"] == cfg.AS, int["link"] == "client-vpn") + "\n"
    config = config + defineOSPFConfig(router, cfg.AS) + defineBGPConfig(topology, router, cfg.AS) + defineFooter(router)

    return config

def createCfgFile(name, config):
    with open(name, 'w') as f:
        f.write(config)

def deployTopology(topology, directory):
    
    for router in topology["routers"]:
        print(router["name"])
        confFile = utils.getConfigFile(router["name"], directory)
        createCfgFile(confFile, defineRouterConfig(topology,router))
