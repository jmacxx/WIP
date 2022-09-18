import glob
import socket
import hashlib
import codecs
import binascii
import requests
import time
import datetime
import json
import re


class ElectrumServerConn:
    def __init__(self):
        self.electrum_host = '127.0.0.1'
        self.electrum_port = 50001
        self.bufferSize = 8191
        self.latency = 0.01
        if (self.electrum_host != '127.0.0.1'):
            self.latency = 0.1
        try:
            print('Opening connection')
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10)
            self._sock.connect((self.electrum_host, self.electrum_port))
        except ConnectionRefusedError:
            print("Connection Refused")

    def __del__(self):
        self._sock.close()
        print('Closed')

    def clear_inbound_queue(self):
        try:
            self._sock.setblocking(False)
            received_len = len(self._sock.recv(self.bufferSize))
            retries = 400
            while (received_len == self.bufferSize):
                retries = retries - 1
                if (retries == 0):
                    print("junk in the inbound queue for {}".format(MAKERTAKER))
                    break
                time.sleep(self.latency)
                received_len = len(self._sock.recv(self.bufferSize))
        except:
            return

    def do_command(self, packet):
        try:
            self.clear_inbound_queue()
            self._sock.setblocking(True)
            self._sock.send(str.encode(packet))
            response = self._sock.recv(self.bufferSize)
            if (len(response) < self.bufferSize):
                return response.decode('utf-8')
            self.clear_inbound_queue()
        except ConnectionRefusedError:
            print("Connection Refused")
        return "error"


class Bisq:
    def __init__(self):
        self.statistics = {'BUG': 0, 'FLAGGED': 0, 'OK': 0, 'OPEN': 0, 'TOTAL': 0, 'CXL': 0 }
        self.statistics_bsq = {'BUG': 0, 'FLAGGED': 0, 'OK': 0, 'OPEN': 0, 'TOTAL': 0, 'CXL': 0 }
        self.statistics_btc = {'BUG': 0, 'FLAGGED': 0, 'OK': 0, 'OPEN': 0, 'TOTAL': 0, 'CXL': 0 }

    def checkBisqTransactions(self, filename):
        input_file = open(WORKING_DIR + "bisqTradeTxns_" + filename + ".txt", "r")
        output_file = open(WORKING_DIR + "output_" + filename + ".txt", "w")
        log = open(WORKING_DIR + "bisq.log", "w")
        print("processing {}".format(filename))
        for line in input_file:
            line_split = line.strip().split(':')
            if (len(line_split) != 2):
                continue
            txid = line_split[0]
            blockHeight = line_split[1]
            log.write("processBisqTrade: {} blockHeight: {}\n".format(txid, blockHeight))
            status, report = Bisq.processBisqTrade(txid)
            if (report is not None):
                print(report)
                output_file.write(report + "\r\n")
            try:
                self.statistics[status] += 1
                self.statistics["TOTAL"] += 1
                if (filename == 'bsq'):
                    self.statistics_bsq[status] += 1
                    self.statistics_bsq["TOTAL"] += 1
                else:
                    self.statistics_btc[status] += 1
                    self.statistics_btc["TOTAL"] += 1
            except:
                log.write("An exception occurred: {} {}\n".format(txid, status))
        print(self.statistics)
        log.write("\n{}\n".format(self.statistics))
        input_file.close()
        output_file.close()
        log.close()

    def reporting(self):
        # group all flagged txs by deposit tx (trade)
        # sort all trades by date
        path = WORKING_DIR + "output_*.txt"
        sorted_lines = []
        for filename in glob.glob(path):
            with open(filename, 'r') as f:
                for line in f:
                    sorted_lines.append(line)
        sorted_lines.sort()  # sorting by deposit txid in order to group fee payments into trades
        globbed_info, prev_line, trade_date = '', '', ''
        date_keys, sorted_items = [], []
        for line in sorted_lines:
            trade_date = globbed_info[154:164]
            if (line[:30] != prev_line[:30]):   # different deposit txns? -> blank line as group separator
                date_keys.append(trade_date)
                sorted_items.append(globbed_info + "\r\n")
                globbed_info = ""
            globbed_info += line
            prev_line = line
        date_keys.append(trade_date)
        sorted_items.append(globbed_info + "\r\n")
        lst_tuple = list(zip(date_keys, sorted_items))
        lst_tuple.sort(reverse=True)    # now sort by date
        with open(WORKING_DIR + "report.txt", "w") as report:
            total_value = 0.0
            for values in lst_tuple:
                report.write(values[1])
                trade_amount = re.compile('(?<=value=)([^\n\r]*)').findall(values[1])
                if (len(trade_amount) > 0):
                    total_value += float(trade_amount[0])
            report.write("\r\n")
            report.write("{} fee payment txs analyzed\r\n".format(self.statistics["TOTAL"]))
            report.write("{} trades analyzed\r\n".format(int(self.statistics["TOTAL"] / 2)))
            report.write("{} trades with locked/abandoned multisig\r\n".format(len(lst_tuple)))
            report.write("{} of {} BSQ fee payments resulting in cancel offer or failed trade\r\n".format(self.statistics_bsq["CXL"], self.statistics_bsq["TOTAL"]))
            report.write("{} of {} BTC fee payments resulting in cancel offer or failed trade\r\n".format(self.statistics_btc["CXL"], self.statistics_btc["TOTAL"]))
            report.write("{} of {} BSQ fee payments resulting in locked multisig\r\n".format(self.statistics_bsq["FLAGGED"], self.statistics_bsq["TOTAL"]))
            report.write("{} of {} BTC fee payments resulting in locked multisig\r\n".format(self.statistics_btc["FLAGGED"], self.statistics_btc["TOTAL"]))
            report.write("{} BTC total locked value\r\n".format(total_value))
            report.close()

    @staticmethod
    def processBisqTrade(maker_or_taker_tx_id):
        global MAKERTAKER
        MAKERTAKER = maker_or_taker_tx_id
        report = None
        deposit_txid, value = Bisq.getOutputTxId(maker_or_taker_tx_id, 1)
        if (deposit_txid is None):
            return "OPEN", report
        validDepositTx, date = Bisq.validateDepositTransaction(deposit_txid)
        if (date is not None and (date < 1577858400 or date > 1654059600)):  # before 2020-01 or after 2022-06 ignored
            return "OK", report
        if (not validDepositTx):
            return "CXL", report
        payout_txid, value = Bisq.getOutputTxId(deposit_txid, 0)
        if (payout_txid is None):
            report = "deposit={} feePayment={} date={} value={}".format(
                deposit_txid, maker_or_taker_tx_id, datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d'), value)
            return "FLAGGED", report
        elif (payout_txid.startswith("CXL")):
            return payout_txid, report
        elif (len(payout_txid) == 64):
            return "OK", report
        return "BUG", report

    @staticmethod
    def validateDepositTransaction(depositTxid):
        # must have 2 inputs
        # must have exactly 1 output (newer version), older version has an OP_RETURN as 2nd output
        # the output should be to a P2WSH script
        tx_info = Bisq.getTransactionJson(depositTxid)
        if (tx_info is None):
            return False, None            # means the tx is really large, we could not load it
        date = tx_info['time']
        if (len(tx_info['vin']) != 2):
            return False, date
        # the two inputs must be from different origin txs
        if (len(tx_info['vout']) == 2 or len(tx_info['vout']) == 3):
            if (int(tx_info['vout'][1]['value']) != 0):
                return False, date
        elif (len(tx_info['vout']) != 1):
            return False, date
        script_pub_key = tx_info['vout'][0]['scriptPubKey']['hex']
        # Bisq multisig is P2WSH (0020), old version is P2SH (a914.....87)
        if (not script_pub_key.startswith('0020') and not script_pub_key.startswith('a914')):
            return False, date
        if (script_pub_key.startswith('a914')):
            # second output needs to be an OP_RETURN (nulldata) when first output is P2SH (Bisq prior to segwit)
            if (len(tx_info['vout']) < 2 or not tx_info['vout'][1]['scriptPubKey']['asm'].startswith("OP_RETURN")):
                return False, date
        tx_origin1 = tx_info['vin'][0]['txid']
        tx_origin2 = tx_info['vin'][1]['txid']
        if (tx_origin1 == tx_origin2):
            return False, date
        return True, date

    @staticmethod
    def getOutputTxId(txid, outputIndex):
        tx_info = Bisq.getTransactionJson(txid)
        if (tx_info is None or len(tx_info['vout']) < 1 + outputIndex):
            return None, None
        addressscript_hex = tx_info['vout'][outputIndex]['scriptPubKey']['hex']
        value = tx_info['vout'][outputIndex]['value']
        if (addressscript_hex in KNOWN_FEE_RECEIVERS):
            return "CXL", None
        script_hash = bytes(hashlib.sha256(codecs.decode(addressscript_hex, 'hex_codec')).digest())
        script_hash = binascii.hexlify(bytes(reversed(script_hash))).decode('ascii')
        if (script_hash in IGNORED_SCRIPT_HASHES):
            print("got a banned scripthash {} {}".format(addressscript_hex, len(IGNORED_SCRIPT_HASHES)))
            return "CXL", None
        try:
            packet = '{ "method":"blockchain.scripthash.get_history", "id":"1234", "params":["' + script_hash + '"] }\n'
            j = json.loads(ELECTRUM.do_command(packet))
            if (len(j["result"]) > 0):
                date = j["result"][0]['height']     # trade date (blockheight)
            if (len(j["result"]) < 2):
                return None, value            # scripthash history shows no payout
        except:
            IGNORED_SCRIPT_HASHES.add(script_hash)
            return "CXL", None           # scripthash history was too large, usually means an exchange address
        try:
            output_txid = j["result"][1]['tx_hash']
        except:
            return None, None
        return output_txid, value

    @staticmethod
    def getTransactionJson(txid):
        try:
            packet = '{ "method":"blockchain.transaction.get", "id":"1234", "params":["' + txid + '", true] }\n'
            j = json.loads(ELECTRUM.do_command(packet))
            if (len(j["result"]) < 2):
                return None
            tx_json = j["result"]
            return tx_json
        except:
            return None

    @staticmethod
    def generateListOfBisqTransactions(address, last_known_txid=""):
        f = open(WORKING_DIR + "bisqTradeTxns_" + address + ".txt", "a")
        for i in range(500):
            url = "https://mempool.space/api/address/" + address + "/txs/chain/" + last_known_txid
            j = requests.get(url).json()
            print("request:{} txids:{}".format(i, len(j)))
            if (len(j) == 0):
                break
            for txidInfo in j:
                last_known_txid = txidInfo['txid']
                blockHeight = txidInfo['status']['block_height']
                f.write("{}:{}\n".format(last_known_txid, blockHeight))
            f.flush()
            time.sleep(1)  # don't overload the web API
        f.close()


if __name__ == "__main__":
    global WORKING_DIR
    WORKING_DIR = ""
    global ELECTRUM
    ELECTRUM = ElectrumServerConn()
    # IGNORED_SCRIPT_HASHES is built dynamically when getting history for an address that has been reused too much,
    # (e.g. an exchange wallet). those addresses are too large to be read using electrum server
    global IGNORED_SCRIPT_HASHES
    IGNORED_SCRIPT_HASHES = set()

    global KNOWN_FEE_RECEIVERS
    KNOWN_FEE_RECEIVERS = ['a9144bc07b10e86df307c408da115896a0e8293c24c487', # 38bZBj5peYS3Husdz7AH3gEUiUbYRD951t BTC fee addr
        '76a914732b213f56728395cbc738fb3c8b3d9649aa672988ac',                # 1BVxNn3T12veSK6DgqwU4Hdn7QHcDDRag7 BM2018
        'a91490c4687b1c28e2c1e9a00408ba1e8ed152863eda87',                    # 3EtUWqsGThPtjwUczw27YCo6EWvQdaPUyp BM2019
        'a9145c95d9cf9d48683284dff53379acc296eb21488387',                    # 3A8Zc1XioE2HRzYfbb5P8iemCS72M6vRJV BM2
        'a9141eb2afdea60e402a78506e75987d188b19462de287',                    # 34VLFgtFKAtwTdZ5rengTT2g2zC99sWQLC BM3
        '76a914921af55494ada420b6aec5b9dd7a701fb0a808a988ac',                # 1EKXx73oUhHaUh8JBimtiPGgHfwNmxYKAj
        '76a914b892929f84ea2c2ed334753a8a472b063b100dc688ac',                # 1HpvvMHcoXQsX85CjTsco5ZAAMoGu2Mze9
        'a9148e4c4aa66b700598b1e08a5706fcbeba6f26839987',                    # 3EfRGckBQQuk7cpU7SwatPv8kFD1vALkTU
        '76a9141f9342d9da1d15683076188c92f361ba2d6537ab88ac',                # 13sxMq8mTw7CTSqgGiMPfwo6ZDsVYrHLmR
        '76a91460dc8093a81ddbd62850d71399bc4322f249cde288ac',                # 19qA2BVPoyXDfHKVMovKG7SoxGY7xrBV8c
        '76a91459b749753293b3b46b6f7e35a27119c0e2974a8488ac']                # 19BNi5EpZhgBBWAt5ka7xWpJpX2ZWJEYyq

#    Bisq.generateListOfBisqTransactions("38bZBj5peYS3Husdz7AH3gEUiUbYRD951t")
#    Bisq.generateListOfBisqTransactions("3EtUWqsGThPtjwUczw27YCo6EWvQdaPUyp")
#    Bisq.generateListOfBisqTransactions("3A8Zc1XioE2HRzYfbb5P8iemCS72M6vRJV")
#    Bisq.generateListOfBisqTransactions("1EKXx73oUhHaUh8JBimtiPGgHfwNmxYKAj")
#    Bisq.generateListOfBisqTransactions("1HpvvMHcoXQsX85CjTsco5ZAAMoGu2Mze9")
#    Bisq.generateListOfBisqTransactions("3EfRGckBQQuk7cpU7SwatPv8kFD1vALkTU")
#    Bisq.generateListOfBisqTransactions("13sxMq8mTw7CTSqgGiMPfwo6ZDsVYrHLmR")
#    Bisq.generateListOfBisqTransactions("19qA2BVPoyXDfHKVMovKG7SoxGY7xrBV8c")
#    Bisq.generateListOfBisqTransactions("19BNi5EpZhgBBWAt5ka7xWpJpX2ZWJEYyq")

    bisq = Bisq()
    bisq.checkBisqTransactions("bsq")
    bisq.checkBisqTransactions("38bZBj5peYS3Husdz7AH3gEUiUbYRD951t")
    bisq.checkBisqTransactions("3EtUWqsGThPtjwUczw27YCo6EWvQdaPUyp")
    bisq.checkBisqTransactions("3A8Zc1XioE2HRzYfbb5P8iemCS72M6vRJV")
    bisq.checkBisqTransactions("1EKXx73oUhHaUh8JBimtiPGgHfwNmxYKAj")
    bisq.checkBisqTransactions("1HpvvMHcoXQsX85CjTsco5ZAAMoGu2Mze9")
    bisq.checkBisqTransactions("3EfRGckBQQuk7cpU7SwatPv8kFD1vALkTU")
    bisq.checkBisqTransactions("13sxMq8mTw7CTSqgGiMPfwo6ZDsVYrHLmR")
    bisq.checkBisqTransactions("19qA2BVPoyXDfHKVMovKG7SoxGY7xrBV8c")
    bisq.checkBisqTransactions("19BNi5EpZhgBBWAt5ka7xWpJpX2ZWJEYyq")
    bisq.reporting()
