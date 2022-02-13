import generateConfigFile as s
import utils
import cfg

PROJECT_DIR = "/home/abdel/GNS3/projects/test_script/project-files/dynamips/"



def main() :
    data = utils.getTopology('data.v2.json')
    s.deployTopology(data, PROJECT_DIR)
    #print(s.defineRouterConfig(data,data["routers"][3]))
    #print(s.defineRouterConfig(data,data["routers"][0]))
    #print(s.defineVRFConfig(data["routers"][0]))
    #print(s.defineVRFConfig(data["routers"][3]))


if __name__ == "__main__": 
    main()
