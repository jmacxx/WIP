import time
import subprocess
import json
import os
from os import listdir
from os.path import isfile, isdir, join
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

JSON_PATH = "/home/coxjma/.local/share/bisq-inventory-monitor-BTC_MAINNET/json"


if __name__ == '__main__':

    seednode = "devinsn3xu"
    mypath = JSON_PATH+"/"+seednode
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles.sort()
    if (len(onlyfiles) > 0):
        fname = onlyfiles[len(onlyfiles)-1]
        _ = open(mypath+"/"+fname, 'r'); data = _.read().replace('\n',' '); _.close()
        # check the json for alerts
        j = json.loads(data)
        for key, val in j["dataMap"].items():
            if key == "daoStateChainHeight":
                if val["persistentAlert"] == False:
                    print(f'introducing test alert: {key}')
                    j["dataMap"][key]["persistentAlert"] = True
                    print(j["dataMap"][key])
        writefilepath = mypath+"/"+fname
        print(f'writing to file: {writefilepath}')
        with open(writefilepath, 'w') as f:
            json.dump(j, f)
            f.close()
        os.system(f"touch {mypath}")
        
