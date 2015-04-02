__author__ = 'luke Berezynskyj <eat.lemons@gmail.com>'


import os
import sys
import json
import urllib
import urllib2
import logging as logger
import subprocess


def wav_to_flac(wav=None):
    if os.path.isfile(wav):
        logger.info("Converting %s to flac" % wav)
        flac = '%s.flac' % wav[:-4]
        subprocess.check_call(['sox', wav, flac])
        logger.info("Converted %s to %s" % (wav, flac))
        return flac
    else:
        logger.error("Could not convert %s to flac" % wav)


def convert(filename=None, api_key=None):
    url = "https://www.google.com/speech-api/v2/recognize?output=json&lang=en&key=%s" % api_key
    audio = open(filename, 'rb').read()
    headers = {'Content-Type': 'audio/x-flac; rate=8000', 'User-Agent': 'Mozilla/5.0'}
    logger.info("Sending request for %s" % filename)
    try:
        request = urllib2.Request(url, data=audio, headers=headers)
        response = urllib2.urlopen(request)
        response = response.read()
        response = response.split('\n', 1)[1]
        full = json.loads(response)
        match = json.loads(response)['result'][0]['alternative'][0]['transcript']
        return (full, match)
    except Exception as e:
        logger.exception(e)
    return False


def get_text(wav):
    flac = wav_to_flac(wav)
    result = convert(flac)
    os.remove(flac)
    return result