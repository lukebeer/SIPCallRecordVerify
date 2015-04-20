__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import sys
import time
import json
import socket
import logging
import pjsua as pj
import multiprocessing
from time import sleep
from verify import Verify
from optparse import OptionParser
from accounthandler import AccountHandler


logging.basicConfig(level=logging.DEBUG, format="%(message)s")


class SIPCallRecordVerify:
    ua_cfg = pj.UAConfig()
    ua_cfg.max_calls = 10
    ua_cfg.nameserver = ["8.8.8.8"]
    ua_cfg.user_agent = "SIPCallRecordVerify"

    media_cfg = pj.MediaConfig()
    media_cfg.channel_count = 8
    media_cfg.max_media_ports = 8

    def __init__(self, caller, calling, log_level=3):
        self.verify = Verify()
        if not self.verify.setup():
            sys.exit(1)
        self.lib = pj.Lib()
        self.lib.init(ua_cfg=self.ua_cfg,
                     log_cfg=pj.LogConfig(level=7, callback=lambda level, str, len: logging.debug(str.strip())),
                     media_cfg=self.media_cfg)
        self.lib.start(with_thread=True)
        self.caller_ddi, self.caller_account, self.caller_cb, self.caller_cfg = self.register(caller, default=True)
        self.calling_ddi, self.calling_account, self.calling_cb, self.calling_cfg = self.register(calling)

    def register(self, config, default=False):
        for k, v in config.iteritems():
            config[k] = str(v)
        ddi = config['ddi']
        logging.info("Creating transport for %s" % (config['uri']))
        transport = self.lib.create_transport(pj.TransportType.UDP)
        logging.info("Listening on %s:%d for %s" % (transport.info().host, transport.info().port, config['uri']))
        logging.info("Attempting registration for %s" % config['uri'])
        account_cfg = pj.AccountConfig(domain=config['domain'], username=config['username'],
                                   password=config['password'], proxy=config['proxy'])
        account_cfg.id = config['uri']
        account = self.lib.create_account(acc_config=account_cfg, set_default=default)
        account.set_transport(transport)
        account_cb = AccountHandler(account)
        account.set_callback(account_cb)
        account_cb.wait()
        logging.info("%s registered, status: %s (%s)" % (config['uri'], account.info().reg_status, account.info().reg_reason))
        return (ddi, account, account_cb, account_cfg)

    def start_caller(self, audiotest, interval=300):
        try:
            call = None
            end = time.time() + interval
            while True:
                if call:
                    while call.is_valid():
                        logging.info("Call in progress")
                        sleep(1)
                        continue
                remaining = end - time.time()
                logging.info("Seconds until next call: %d" % remaining)
                if time.time() <= end:
                    sleep(1)
                    continue
                end = time.time() + interval
                logging.info("Making call")
                call, callhandler = self.caller_cb.new_call("%s@%s" % (self.calling_ddi, self.caller_cfg.proxy[0][4:-3]))
                if call:
                    while call.info().state != pj.CallState.CONFIRMED:
                        logging.info("Looping call state check with %s" % call.info().state)
                        sleep(1)
                        continue
                    sleep(1)
                    callhandler.play_file(audiotest['filename'], True)
                    # TODO: Fetch recording, convert to text, validate.
                    sleep(1)
                    call.hangup()
                sleep(1)
        except pj.Error, e:
            logging.error("Exception: " + str(e))


    def run(self, audiotest, interval=300):
        try:
            caller = multiprocessing.Process(target=self.start_caller, args=(audiotest, interval))
            caller.start()
            caller.join()
        except pj.Error, e:
            logging.error("Exception: " + str(e))
        finally:
            self.lib.destroy()


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-c', dest='config',    help="eg: server_one.json", default="config.json")
    op.add_option('-i', dest='interval',  help="Test interval in seconds (default: 5min)", default=5, type="int")
    op.add_option('-t', dest='threshold', help="Minimum threshold percent that recording is valid (default: 80)", default=80, type="int")
    op.add_option('-v', dest='log_level', help="Be verbose with logging", default=3, type="int")
    (opts, args) = op.parse_args()
    config = json.load(file(opts.config))
    app = SIPCallRecordVerify(config['sip']['caller'], config['sip']['calling'], opts.log_level)
    app.run(config['audiotest'], opts.interval)
