__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import sys
import time
import json
import logging
import pjsua as pj
from time import sleep
from verify import Verify
from optparse import OptionParser
from accounthandler import AccountHandler


lib = pj.Lib()
log_level = logging.INFO
logging.basicConfig(level=logging.INFO, format="%(message)s")


class SIPCallRecordVerify:
    ua_cfg = pj.UAConfig()
    ua_cfg.max_calls = 10
    ua_cfg.nameserver = ["8.8.8.8"]
    ua_cfg.user_agent = "SIPCallRecordVerify"

    media_cfg = pj.MediaConfig()
    media_cfg.channel_count = 8
    media_cfg.max_media_ports = 8

    def __init__(self, uri, domain=None, username=None, password=None, proxy=None):
        self.verify = Verify()
        if not self.verify.setup():
            sys.exit(1)
        self.uri = uri
        self.username = username
        self.password = password
        self.domain = domain
        self.proxy = proxy
        global lib
        lib.init(ua_cfg=self.ua_cfg,
                     log_cfg=pj.LogConfig(level=log_level, callback=lambda level, str, len: logging.debug(str.strip())),
                     media_cfg=self.media_cfg)
        transport = lib.create_transport(pj.TransportType.UDP)
        logging.info("Listening on %s:%d" % (transport.info().host, transport.info().port))
        lib.start(with_thread=True)
        logging.info("Attempting registration...")
        acc_cfg = pj.AccountConfig(domain=self.domain, username=self.username, password=self.password, proxy=self.proxy)
        acc_cfg.id = self.uri
        self.acc = lib.create_account(acc_config=acc_cfg)
        self.acc_cb = AccountHandler(self.acc)
        self.acc.set_callback(self.acc_cb)
        self.acc_cb.wait()
        logging.info("Registration complete, status: %s (%s)" % (self.acc.info().reg_status, self.acc.info().reg_reason))
        logging.info("Max conf ports: %s" % lib.conf_get_max_ports())

    def run(self, dial_ddi, audiotest, interval=300):
        global lib
        try:
            call = None
            end = time.time() + interval
            while True:
                remaining = end - time.time()
                logging.info("Seconds until next call: %d" % remaining)
                if time.time() >= end:
                    end = time.time() + interval
                    if call:
                        if call.is_valid():
                            continue
                    logging.info("Making call")
                    call, callhandler = self.acc_cb.new_call("%s@%s" % (dial_ddi, self.proxy[4:]))
                    if call:
                        while call.info().state != pj.CallState.CONFIRMED:
                            continue
                        sleep(1) #  Be gentle, we could be dealing with Windows.
                        callhandler.play_file(audiotest['filename'], True)
                        # TODO: Fetch recording, convert to text, validate.
                        sleep(1)
                        call.hangup()
                sleep(1)
                sys.stdout.flush()
                lib.handle_events()
        except pj.Error, e:
            logging.error("Exception: " + str(e))
        finally:
            lib.destroy()


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-c', dest='config', help="eg: server_one.json", default="config.json")
    op.add_option('-i', dest='interval', help="Test interval in seconds (default: 5min)", default=300)
    op.add_option('-t', dest='threshold', help="Minimum threshold percent that recording is valid (default: 80)", default=80)
    op.add_option('-v', dest='verbose', help="Be verbose with logging", default=False)
    (opts, args) = op.parse_args()
    config = json.load(file(opts.config))
    sip = config['sip']
    app = SIPCallRecordVerify(uri=str(sip['uri']), domain=str(sip['domain']), username=str(sip['username']),
                              password=str(sip['password']), proxy=str(sip['proxy']))
    app.run(str(sip['dial_ddi']), str(config['audiotest']), opts.interval)
