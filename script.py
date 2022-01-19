import json




"""def defineEntete(hostname):
    entete = "!"
    entete = entete + "hostname " + hostname
    entete = entete + "fin entete"

    return

def defineIP(interface):
    blockIp = ""

    return blockIp"""

def getTopology(file):
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data


def main() :
    #print(getTopology('data.json'))
    print ('!\n' *7)


if __name__ == "__main__" : 
    main()