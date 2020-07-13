#!/usr/bin/python

import json
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