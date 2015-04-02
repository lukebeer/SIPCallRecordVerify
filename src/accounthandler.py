__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import re
import logging
import threading
import pjsua as pj
from callhandler import CallHandler


class AccountHandler(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        global lib
        lib = pj.Lib.instance()
        lib.set_null_snd_dev()
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        logging.info("Reg state: %s" % str(self.account.info().reg_status))
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

    def on_incoming_call(self, call):
        global lib
        dn_match = None
        logging.info("Call recieved: %s" % call)
        call_handler = CallHandler(call)
        call_handler.set_account(self)
        call.answer()
        call.set_callback(call_handler)
        lib.conf_connect(call.info().conf_slot, 0)
        lib.conf_connect(0, call.info().conf_slot)
        dn_match = re.match("sip:(\d+)@", call.info().remote_uri)
        call.hangup()

    def new_call(self, uri, joining_slot=None):
        global lib
        logging.info("Attempting new call to %s" % uri)
        try:
            call_handler = CallHandler()
            call = self.account.make_call("sip:%s" % uri, call_handler)
            if joining_slot:
                while call.info().media_state != pj.MediaState.ACTIVE:
                    continue
                lib.conf_connect(joining_slot, call.info().conf_slot)
                lib.conf_connect(call.info().conf_slot, joining_slot)
            return (call, call_handler)
        except pj.Error, e:
            print "Exception: " + str(e)
            return None