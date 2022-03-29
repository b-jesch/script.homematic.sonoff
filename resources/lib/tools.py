#!/usr/bin/python

import re
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

from contextlib import contextmanager

ADDON = xbmcaddon.Addon(id='script.homematic.sonoff')
ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')
PATH = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
PROFILE = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
LS = xbmcaddon.Addon().getLocalizedString

# Constants

STRING = 0
BOOL = 1
NUM = 2


def writeLog(message, level=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (xbmcaddon.Addon().getAddonInfo('id'),
                             xbmcaddon.Addon().getAddonInfo('version'),
                             message), level)


def notify(header, message, icon=xbmcgui.NOTIFICATION_INFO, dispTime=5000):
    xbmcgui.Dialog().notification(header, message, icon=icon, time=dispTime)


def dialogOK(header, message):
    xbmcgui.Dialog().ok(header, message)


def strToBool(par):
    return True if par.upper() == 'TRUE' else False


def getAddonSetting(setting, sType=STRING, multiplicator=1):
    if sType == BOOL:
        return strToBool(xbmcaddon.Addon().getSetting(setting))
    elif sType == NUM:
        try:
            return int(re.match('\d+', xbmcaddon.Addon().getSetting(setting)).group()) * multiplicator
        except AttributeError:
            return 0
    else:
        return xbmcaddon.Addon().getSetting(setting)


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