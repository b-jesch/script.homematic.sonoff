#!/usr/bin/python

import json
import platform
import subprocess
import os
import re

import xbmc
import xbmcgui
import xbmcaddon

from contextlib import contextmanager

ADDON = xbmcaddon.Addon(id='script.homematic.sonoff')
ADDON_NAME = ADDON.getAddonInfo('name')
PATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
LS = ADDON.getLocalizedString

# Constants

STRING = 0
BOOL = 1
NUM = 2


def writeLog(message, level=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (ADDON.getAddonInfo('id'),
                             ADDON.getAddonInfo('version'),
                             message), level)

def notify(header, message, icon=xbmcgui.NOTIFICATION_INFO, dispTime=5000):
    xbmcgui.Dialog().notification(header, message, icon=icon, time=dispTime)


def release():
    item = {}
    coll = {'platform': platform.system(), 'hostname': platform.node()}
    if coll['platform'] == 'Linux':
        with open('/etc/os-release', 'r') as _file:
            for _line in _file:
                parameter, value = _line.split('=')
                item[parameter] = value.replace('"', '').strip()

    coll.update({'osname': item.get('NAME', ''), 'osid': item.get('ID', ''), 'osversion': item.get('VERSION_ID', '')})
    return coll


def getProcessPID(process):
    if not process: return False
    OS = release()
    if OS['platform'] == 'Linux':
        _syscmd = subprocess.Popen(['pidof', process], stdout=subprocess.PIPE)
        PID = _syscmd.stdout.read().strip()
        return PID if PID > 0 else False
    elif OS['platform'] == 'Windows':
        _tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % os.path.basename(process)
        _syscmd = subprocess.Popen(_tlcall, shell=True, stdout=subprocess.PIPE)
        PID = _syscmd.communicate()[0].strip().split('\r\n')
        if len(PID) > 1 and os.path.basename(process) in PID[-1]:
            return PID[-1].split()[1]
        else: return False
    else:
        writeLog('Running on {}, could not determine PID of {}'.format(OS, process))
        return False


def dialogOK(header, message):
    xbmcgui.Dialog().ok(header.encode('utf-8'), message.encode('utf-8'))


def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(querystring, encoding='utf-8')))
        if 'result' in response: return response['result']
    except TypeError, e:
        writeLog('Error executing JSON RPC: {}'.format(e.message), xbmc.LOGFATAL)
    return None


def strToBool(par):
    return True if par.upper() == 'TRUE' else False


def getAddonSetting(setting, sType=STRING, multiplicator=1):
    if sType == BOOL:
        return strToBool(ADDON.getSetting(setting))
    elif sType == NUM:
        try:
            return int(re.match('\d+', ADDON.getSetting(setting)).group()) * multiplicator
        except AttributeError:
            return 0
    else:
        return ADDON.getSetting(setting)


def setAddonSetting(setting, value, sType=STRING):
    if sType == BOOL:
        ADDON.setSetting(setting, str(value).lower())
    else:
        ADDON.setSetting(setting, str(value))


@contextmanager
def busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')