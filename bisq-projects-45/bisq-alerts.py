# The bisq-alerts process monitors updates to the json directory.  When new
# files are deposited (which happens randomly) it analyzes them to see if any
# new alerts are indicated or if any prior alerts have de-escalated.
# This process maintains state information about the currently active alerts
# in a file 'alerts.json', which is also served to http clients via
# the bisq-monitor-app process.
# Whenever an alert is added or removed, a Keybase message is sent to
# notify operators.

# There is a lot more nuance to how this works.
# This process has to watch a directory for file creation events.  The events
# received happen before the Java process has finished writing data, and there
# are multiple events fired per file.  So a "cool-off" period is used such 
# that we do not analyze the data until at least 4 seconds have passed since 
# the last activity.
# Files received from the Java monitor are stored using a unix timestamp
# as the filename.  In order to get the most recent file we sort them all and
# pick the last in the list.


import time
import datetime
import subprocess
import json
import os
from os import listdir
from os.path import isfile, isdir, join
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

JSON_PATH = "/home/tmpmonitorbot45/.local/share/bisq-inventory-monitor-BTC_MAINNET/json"
KEYBASE_RECIPIENTS = "jmacxx,chimp1984"


class Watcher:
    DIRECTORY_TO_WATCH = JSON_PATH

    def __init__(self):
        self.observer = Observer()
        self.alertManager = AlertManager()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
                aggregates = event_handler.extractUpdates()
                nProcessed = 0
                for val in aggregates:
                    nProcessed += self.alertManager.checkNodeAlerts(val)
                if nProcessed > 0:
                    self.alertManager.writeJson()
                    
        except Exception as e:
            self.observer.stop()
            print(e)

        self.observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self):
        self.aggregates = set()
        self.lastUpdate = time.time()

    def extractUpdates(self):
        timeNow = time.time()
        if timeNow - self.lastUpdate < 4:
            return set()
        retVal = self.aggregates
        self.aggregates = set()
        return retVal

    def on_any_event(self, event):
        if event.is_directory:
            #print("Received directory event - %s." % event.src_path)
            splitString = event.src_path.split("/")
            seednode = splitString[len(splitString)-1]
            self.aggregates.add(seednode)
            self.lastUpdate = time.time()

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            #print("Received created event - %s." % event.src_path)
            pass
        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            #print("Received modified event - %s." % event.src_path)
            pass

class AlertManager():

    def __init__(self):
        with open(JSON_PATH+"/alerts.json", "r") as read_file:
            print("loading JSON from file: " + JSON_PATH + "/alerts.json")
            self.nodeAlerts = json.load(read_file)

    def writeJson(self):
        with open(JSON_PATH+"/alerts.json", "w") as outfile:  
            print("writing JSON file: " + JSON_PATH + "/alerts.json")
            json.dump(self.nodeAlerts, outfile) 

    def checkNodeAlerts(self, seednode):
        mypath = JSON_PATH+"/"+seednode
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        onlyfiles.sort()
        retVal = 0
        if (len(onlyfiles) > 0):
            fname = onlyfiles[len(onlyfiles)-1]
            _ = open(mypath+"/"+fname, 'r'); data = _.read().replace('\n',' '); _.close()
            knownAlerts = dict()
            if seednode in self.nodeAlerts:
                knownAlerts = self.nodeAlerts[seednode]
            # check the json for alerts
            j = json.loads(data)
            if "errorMessage" in j:
                print(f'{seednode}: {j["errorMessage"]}')
                self.notifyAlertStarted(seednode, knownAlerts, "OFFLINE", j["errorMessage"], j["requestStartTime"])
            else:
                if "OFFLINE" in knownAlerts:
                    knownAlerts.pop("OFFLINE")
                    self.notifyAlertStopped(seednode, "OFFLINE", "n/a")
                for key, val in j["dataMap"].items():
                    if val["persistentAlert"] == True:
                        print(f'active alert: {key}')
                        self.notifyAlertStarted(seednode, knownAlerts, key, val["value"], j["requestStartTime"])
                    else:
                        # non-alerting key, see whether it can kill an existing alert
                        if key in knownAlerts:
                            knownAlerts.pop(key)
                            self.notifyAlertStopped(seednode, key, val["value"])
            self.nodeAlerts[seednode] = knownAlerts
            print(f'{len(knownAlerts)} alerts for {seednode}')
            retVal += 1
        return retVal

    def notifyAlertStarted(self, seednode, knownAlerts, alertingField, alertingValue, javaTimestamp):
        epochTimestamp = self.toEpochTime(javaTimestamp)
        if alertingField not in knownAlerts:
            knownAlerts[alertingField] = { "value": alertingValue, "startTimestamp": epochTimestamp, "sentToKeybase": 0 }
            now = datetime.datetime.fromtimestamp(epochTimestamp)
            timestr = now.strftime("%H:%M:%S")
            print(f'alert started: {seednode}/{alertingField} @ {timestr}')
        notifyKeybase = True if knownAlerts[alertingField]["sentToKeybase"] == 0 else False
        # special consideration for offline alert.  We don't receive any indication from Java about
        # the "persistentAlert" status.  So as a crude workaround we only alert keybase if this
        # alert age is > 10 minutes
        if alertingField == "OFFLINE":
            alertAge = epochTimestamp - knownAlerts[alertingField]["startTimestamp"]
            if (alertAge / 60 < 10):
                print(f'received OFFLINE alert age={alertAge}, but lets wait until it is 10 minutes old before notifying')
                notifyKeybase = False
        if notifyKeybase:
            knownAlerts[alertingField]["sentToKeybase"] += 1
            print(f'sending alert {seednode}/{alertingField} to keybase')
            os.system(f'keybase chat send {KEYBASE_RECIPIENTS} "🆘 alert started: {seednode} => {alertingField}={alertingValue} @ {timestr}"')

    def notifyAlertStopped(self, seednode, alertingField, value):
        now = datetime.datetime.now()
        timestr = now.strftime("%H:%M:%S")
        print(f'alert stopped: {seednode}/{alertingField}')
        os.system(f'keybase chat send {KEYBASE_RECIPIENTS} "🆗 alert ended: {seednode} => {alertingField}={value} @ {timestr}"')

    def toEpochTime(self, timestamp):
        # removes milliseconds from Java timestamp
        s = str(timestamp)
        return int(s[0:len(s)-3])
        

if __name__ == '__main__':
    now = datetime.datetime.now()
    timestr = now.strftime("%H:%M:%S")
    os.system(f'keybase chat send {KEYBASE_RECIPIENTS} "seednode alert monitor starting up @ {timestr}"')
    w = Watcher()
    w.run()


