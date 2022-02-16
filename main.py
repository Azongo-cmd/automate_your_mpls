import generateConfigFile as s
import utils
import cfg
import sys



def main() :

    data = utils.getTopology('data.v2.json')
    if len(sys.argv) < 2:
        print('No argument. Add : \n - reset to reset topology \n - deploy to deploy topology')
    else:
        if(sys.argv[1] == 'deploy'):
            s.deployTopology(data, cfg.PROJECT_DIR)
        elif (sys.argv[1] == 'reset'):
            s.resetTopology(data, cfg.PROJECT_DIR)
        else:
            print('Bad argument. Add : \n - reset to reset topology \n - deploy to deploy topology')



if __name__ == "__main__": 
    main()
