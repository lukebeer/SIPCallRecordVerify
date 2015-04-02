__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import re
import logging
import subprocess
import pjsua as pj
from time import sleep


class CallHandler(pj.CallCallback):
    def __init__(self, call=None):
        global lib
        lib = pj.Lib.instance()
        pj.CallCallback.__init__(self, call)
        self.wait_for_hash = False
        self.collection = ''
        self.action = None
        self.account = None

    def set_account(self, account):
        self.account = account

    def play_file(self, file="default.wav", enforce_playback=False):
        global lib
        logging.info("Playing file %s" % file)
        player = lib.create_player(file)
        player_slot = lib.player_get_slot(player)
        lib.conf_connect(player_slot, self.call.info().conf_slot)
        if enforce_playback:
            meta = subprocess.check_output(["sox", file, "-n", "stat"], stderr=subprocess.STDOUT)
            duration = re.search("Length[^\d]+((?:\d|\.)+)", meta).group(1)
            logging.info("Enforcing media playback with duration: %s" % duration)
            sleep(float(duration)+0.6)
            lib.player_destroy(player)
        return player

    def on_state(self):
        logging.info("Call with %s is %s. Last code: %s (%s)" % (self.call.info().remote_uri,
                                                                 self.call.info().state_text,
                                                                 self.call.info().last_code,
                                                                 self.call.info().last_reason))

        if self.call.info().state == pj.CallState.DISCONNECTED:
            logging.info('Call disconnected')

    def on_media_state(self):
        logging.info("Media state: %s" % self.call.info().media_state)
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            logging.info("Media is now active")
        else:
            logging.info("Media is inactive")

    def on_dtmf_digit(self, digits):
        logging.info("Got DTMF digit: %s" % digits)
        pass
        if digits == '#':
            self.wait_for_hash = False
            logging.info("Collected DTMF: %s" % self.collection)
            if self.action == "newcall":
                self.account.new_call(self.collection, self.call.info().conf_slot)
        if self.wait_for_hash:
            self.collection += digits
            return
        if digits == '7':
            self.play_file("default.wav", enforce_playback=True)
            self.wait_for_hash = True
            self.action = "newcall"