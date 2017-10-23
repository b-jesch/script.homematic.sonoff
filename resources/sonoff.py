#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import re

class Sonoff_Switch(object):

    SONOFF_CGI = '/cm'
    STATUS = {'cmnd': 'Power Status'}
    TOGGLE = {'cmnd': 'Power Toggle'}
    ON = {'cmnd': 'Power On'}
    OFF = {'cmnd': 'Power Off'}


    @classmethod
    def select_ip(cls, device):
        return unicode(re.findall(r'[0-9]+(?:\.[0-9]+){3}', device)[0])

    def get_devices(self, devices):
        '''

        :param devices: device list
        :return: dict {device: status (ON|OFF|UNREACHABLE|UNDEFINED}
        '''
        dl = {}
        for d in devices:
            device = self.select_ip(d)
            dl.update({device: self.send_command(device, self.STATUS)})
        return dl

    def send_command(self, device, command):
        device = self.select_ip(device)
        try:
            req = requests.get('http://%s%s' % (device, self.SONOFF_CGI), command)
            req.raise_for_status()
            response = req.text.splitlines()
            for r in response:
                if ' = ' in r:
                    key, val = r.split(' = ')
                    if key == 'RESULT':
                        return json.loads(val, encoding=req.encoding)['POWER']
        except requests.ConnectionError:
            return u'UNREACHABLE'
        except requests.HTTPError:
            return u'UNDEFINED'
        except Exception:
            pass

if __name__ == '__main__':
    device = '192.168.178.11'
    devices = [device, '192.168.178.15', '192.168.178.255']
    sd = Sonoff_Switch()
    print sd.get_devices(devices)
    print sd.send_command(device, sd.TOGGLE)
