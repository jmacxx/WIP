# Python 3 server 
#

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qsl
import time
import re
import requests
import json
import argparse
from os import listdir
from os.path import isfile, isdir, join

JSON_PATH = "/home/tmpmonitorbot45/.local/share/bisq-inventory-monitor-BTC_MAINNET/json"
APP_PATH  = "/home/tmpmonitorbot45/.local/share/bisq-inventory-monitor-BTC_MAINNET/bisqStatsDashboard.html"
#wow2

class ProxyServer(BaseHTTPRequestHandler):
    def do_GET(self):

        if re.search("/seednode_json", self.path) != None:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            parsed_url = urlparse(self.path)
            parsed_qs = dict(parse_qsl(parsed_url.query))
            onlydirs = self.get_latest_dirs()
            snapshot_raw_data = self.get_latest_files(onlydirs)
            j = json.loads(snapshot_raw_data)
            print("sending the results back to caller\n")
            self.wfile.write(bytes(json.dumps(j), "utf-8"))
            
        elif re.search("/app", self.path) != None:
            self.send_response(200)
            self.end_headers()
            _ = open(APP_PATH, 'r'); data = _.read(); _.close()
            print("sending the results back to caller\n")
            self.wfile.write(bytes(data, "utf-8"))

        elif re.search("/alerts", self.path) != None:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            _ = open(JSON_PATH+"/alerts.json", 'r'); data = _.read(); _.close()
            print("sending the results back to caller\n")
            self.wfile.write(bytes(data, "utf-8"))

        elif re.search("/favicon.ico", self.path) != None:
            self.send_response(404)
            
        else:
            self.send_response(404)
            print(f"unexpected request ({self.path}), ignoring")

    def get_latest_dirs(self):
        print("get_latest_dirs")
        onlydirs = [f for f in listdir(JSON_PATH) if isdir(join(JSON_PATH, f))]
        print(onlydirs)
        return onlydirs

    def get_latest_files(self, onlydirs):
        print("get_latest_files")
        retVal = "{"
        iteration=0;
        for seednode in onlydirs:
            mypath = JSON_PATH+"/"+seednode
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            onlyfiles.sort()
            if (len(onlyfiles) > 0):
                fname = onlyfiles[len(onlyfiles)-1]
                if (iteration > 0):
                    retVal = retVal + ','
                iteration = iteration + 1
                retVal = retVal + '"' + seednode + '" : '
                _ = open(mypath+"/"+fname, 'r'); data = _.read().replace('\n',' '); _.close()
                retVal = retVal + data;
        retVal = retVal + "}"
        return retVal
        
        
    def apply_delay(self):
        if ARGS.delay <= 0:
            return
        print("sleeping {} seconds".format(ARGS.delay))
        time.sleep(ARGS.delay)



if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="proxy host", dest="proxy_host", default="46.101.179.224")
    parser.add_argument("--port", help="proxy port", dest="proxy_port", type=int, default=8082)
    parser.add_argument("--delay", help="delay response (seconds)", dest="delay", type=int, default=0)
    parser.add_argument("-v", "--verbose", help="verbose output", action="count", default=0)
    args = parser.parse_args()
    global ARGS
    ARGS = args
    print("ARGS: {}".format(ARGS))

    webServer = HTTPServer((ARGS.proxy_host, ARGS.proxy_port), ProxyServer)
    print("Server started http://%s:%s" % (ARGS.proxy_host, ARGS.proxy_port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


