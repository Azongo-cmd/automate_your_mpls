import generateConfigFile as s
import utils

PROJECT_DIR = "/home/abdel/GNS3/projects/test_script/project-files/dynamips/"



def main() :
    data = utils.getTopology('data.v2.json')
    s.deployTopology(data, PROJECT_DIR)
    #print(s.defineRouterConfig(data,data["routers"][5]))


if __name__ == "__main__": 
    main()