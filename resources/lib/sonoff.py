#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json
import re
import sys

try:
    import tools
except ImportError as e:
    print("module 'tools' not found, redefine...")

    class Tools(object):

        def __init__(self):
            pass

        def writeLog(self, message):
            print(message)


    tools = Tools()

class Sonoff(object):

    TIMEOUT = 3
    SONOFF_CGI = '/cm'
    STATUS = [{'cmnd':'Power Status'}, {'cmnd':'Power2 Status'}, {'cmnd':'Power3 Status'}, {'cmnd':'Power4 Status'}]
    TOGGLE = [{'cmnd':'Power Toggle'}, {'cmnd':'Power2 Toggle'}, {'cmnd':'Power3 Toggle'}, {'cmnd':'Power4 Toggle'}]
    ON = [{'cmnd':'Power On'}, {'cmnd':'Power2 On'}, {'cmnd':'Power3 On'}, {'cmnd':'Power4 On'}]
    OFF = [{'cmnd':'Power Off'}, {'cmnd':'Power2 Off'}, {'cmnd':'Power3 Off'}, {'cmnd':'Power4 Off'}]
    NAME = [{'cmnd':'Status'}, {'cmnd':'Status'}, {'cmnd':'Status'}, {'cmnd':'Status'}]

    @classmethod
    def select_ip(cls, device):
        return re.findall(r'[0-9]+(?:\.[0-9]+){3}', device)[0]

    def send(self, device, command, channel='1', timeout=TIMEOUT):
        device = self.select_ip(device)
        http = urllib3.PoolManager()
        try:
            req = http.request('GET', 'http://%s%s' % (device, self.SONOFF_CGI), fields=command, timeout=timeout)
            result = json.loads(req.data.decode('utf-8'))
            return result.get('POWER', result.get('POWER%s' % channel, result.get('Status', u'UNDEFINED')))
        except IOError as e:
            tools.writeLog('Error: %s' % e.args)
        except ValueError as e:
            tools.writeLog('JSON Response expected, got others: %s' % str(e))
        except Exception as e:
            tools.writeLog('Exception: %s' % e.args)

        return u'UNDEFINED'


if __name__ == '__main__':
    sd = Sonoff()
    try:
        if sys.argv[2].upper() == 'STATUS':
            tools.writeLog(str(sd.send(sys.argv[1], sd.STATUS[int(sys.argv[3])])))
        elif sys.argv[2].upper() == 'NAME':
            tools.writeLog(str(sd.send(sys.argv[1], sd.NAME[int(sys.argv[3])])))
        elif sys.argv[2].upper() == 'TOGGLE':
            tools.writeLog(str(sd.send(sys.argv[1], sd.TOGGLE[int(sys.argv[3])])))
        elif sys.argv[2].upper == 'ON':
            tools.writeLog(str(sd.send(sys.argv[1], sd.ON[int(sys.argv[3])])))
        elif sys.argv[2].upper == 'OFF':
            tools.writeLog(str(sd.send(sys.argv[1], sd.OFF[int(sys.argv[3])])))
        else:
            tools.writeLog('unknown command')
    except IndexError:
        tools.writeLog('not all arguments passed, use "sonoff.py <IP> STATUS|NAME|TOGGLE|ON|OFF <channel (0-3)>"')
