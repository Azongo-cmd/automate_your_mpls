

AS = "100"
CLIENT_COMUNITY = AS + ":1110"
PEER_COMUNITY = AS + ":1120"
PROVIDER_COMUNITY = AS + ":1130"
PROJECT_DIR = "/home/abdel/GNS3/projects/test_script/project-files/dynamips/"

"""
trouver rd

1. est ce que dans client_rd, il y'a un objet que le meme client_name
    Si oui, getObject["last_rd"]+1
    Si non create object et client_rd.append
"""