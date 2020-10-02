#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import sys
from .tools import *

class Sonoff(object):

    TIMEOUT = 3
    SONOFF_CGI = '/cm'
    STATUS = [{'cmnd': 'Power Status'}, {'cmnd': 'Power2 Status'}, {'cmnd': 'Power3 Status'}, {'cmnd': 'Power4 Status'}]
    TOGGLE = [{'cmnd': 'Power Toggle'}, {'cmnd': 'Power2 Toggle'}, {'cmnd': 'Power3 Toggle'}, {'cmnd': 'Power4 Toggle'}]
    ON = [{'cmnd': 'Power On'}, {'cmnd': 'Power2 On'}, {'cmnd': 'Power3 On'}, {'cmnd': 'Power4 On'}]
    OFF = [{'cmnd': 'Power Off'}, {'cmnd': 'Power2 Off'}, {'cmnd': 'Power3 Off'}, {'cmnd': 'Power4 Off'}]
    NAME = [{'cmnd': 'Status'}, {'cmnd': 'Status'}, {'cmnd': 'Status'}, {'cmnd': 'Status'}]

    @classmethod
    def select_ip(cls, device):
        return re.findall(r'[0-9]+(?:\.[0-9]+){3}', device)[0]

    def send(self, device, command, channel='1', timeout=TIMEOUT):

        try:
            req = requests.get('http://%s%s' % (self.select_ip(device), self.SONOFF_CGI),
                               params=command, timeout=timeout)
            req.raise_for_status()
            result = req.json()
            return result.get('POWER', result.get('POWER%s' % channel, result.get('Status', u'UNDEFINED')))
        except (requests.ConnectionError, requests.HTTPError, requests.Timeout) as e:
            writeLog('Error: %s' % e.args, xbmc.LOGERROR)
        except ValueError as e:
            writeLog('JSON Response expected, got others: %s' % str(e), xbmc.LOGERROR)
        except Exception as e:
            writeLog('general Exception: %s' % e.args, xbmc.LOGERROR)

        return u'UNDEFINED'


if __name__ == '__main__':
    sd = Sonoff()
    try:
        if sys.argv[2].upper() == 'STATUS':
            writeLog(str(sd.send(sys.argv[1], sd.STATUS[int(sys.argv[3])])))
        elif sys.argv[2].upper() == 'NAME':
            writeLog(str(sd.send(sys.argv[1], sd.NAME[int(sys.argv[3])])))
        elif sys.argv[2].upper() == 'TOGGLE':
            writeLog(str(sd.send(sys.argv[1], sd.TOGGLE[int(sys.argv[3])])))
        elif sys.argv[2].upper == 'ON':
            writeLog(str(sd.send(sys.argv[1], sd.ON[int(sys.argv[3])])))
        elif sys.argv[2].upper == 'OFF':
            writeLog(str(sd.send(sys.argv[1], sd.OFF[int(sys.argv[3])])))
        else:
            writeLog('unknown command')
    except IndexError:
        writeLog('not all arguments passed, use "sonoff.py <IP> STATUS|NAME|TOGGLE|ON|OFF <channel (0-3)>"')
