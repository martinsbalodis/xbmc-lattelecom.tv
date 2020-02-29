import datetime
import os
import random
import sys

import xbmc
import xbmcaddon
import xbmcplugin

import constants
import utils
from exceptions import ApiError

ADDON = xbmcaddon.Addon()
APPID = xbmcaddon.Addon().getAddonInfo("id")
NAME = xbmcaddon.Addon().getAddonInfo("name")
VERSION = xbmcaddon.Addon().getAddonInfo("version")
ICON = xbmcaddon.Addon().getAddonInfo("icon")
DATADIR=xbmc.translatePath( ADDON.getAddonInfo('profile') )

api_version = 383

# os.uname() is not available on Windows, so we make this optional.
try:
    uname = os.uname()
    os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
    os_string = ''


def get_config(key):
    addon_handle = int(sys.argv[1])
    return xbmcplugin.getSetting(addon_handle, key)


def set_config(key, value):
    addon_handle = int(sys.argv[1])
    return xbmcplugin.setSetting(addon_handle, key, value)


def set_setting(key, value):
    return xbmcaddon.Addon(APPID).setSetting(key, value)


def set_setting_bool(key, value):
    return xbmcaddon.Addon(APPID).setSettingBool(key, value)


def get_setting(key):
    return xbmcaddon.Addon(APPID).getSetting(key)


def get_setting_bool(key):
    return xbmcaddon.Addon(APPID).getSettingBool(key)


class XConfig:
    def __init__(self):
        pass

    @property
    def USERNAME(self): return get_setting(constants.USERNAME)
    @USERNAME.setter
    def USERNAME(self, val): set_setting(constants.USERNAME, val)

    @property
    def PASSWORD(self): return get_setting(constants.PASSWORD)
    @PASSWORD.setter
    def PASSWORD(self, val): set_setting(constants.PASSWORD, val)

    @property
    def TOKEN(self): return get_setting(constants.TOKEN)
    @TOKEN.setter
    def TOKEN(self, val): set_setting(constants.TOKEN, val)

    @property
    def QUALITY(self): return get_setting(constants.QUALITY)
    @QUALITY.setter
    def QUALITY(self, val): self.__UID = set_setting(constants.QUALITY, val)

    @property
    def QUALITYX(self): 
        quality = self.QUALITY
        if utils.isEmpty(quality): quality = 'hd'
        if quality == 'hd': quality = "0-hd"
        elif quality == 'hq': quality = "1-hq"
        elif quality == 'mq': quality = "2-mq"
        elif quality == 'lq': quality = "3-lq"
        return quality

    @property
    def UID(self): return get_setting(constants.UID)
    @UID.setter
    def UID(self, val): self.__UID = set_setting(constants.UID, val)

    @property
    def LAST_LOGIN(self): return get_setting(constants.LAST_LOGIN)
    @LAST_LOGIN.setter
    def LAST_LOGIN(self, val): set_setting(constants.LAST_LOGIN, val)

    @property
    def LOGGED_IN(self): return get_setting_bool(constants.LOGGED_IN)
    @LOGGED_IN.setter
    def LOGGED_IN(self, val): set_setting_bool(constants.LOGGED_IN, val)

    @property
    def SERVICE_ENABLED(self): return get_setting_bool(constants.SERVICE_ENABLED)
    @SERVICE_ENABLED.setter
    def SERVICE_ENABLED(self, val): set_setting_bool(constants.SERVICE_ENABLED, val)

X = XConfig()

def get_unique_id():
    if get_setting(constants.UID) is not None and get_setting(constants.UID) != "":
        return get_setting(constants.UID)

    digits = '0123456789'
    letters = 'abcdef'
    all_chars = digits + letters
    length = 16
    val = None
    while True:
        val = ''.join(random.choice(all_chars) for i in range(length))
        if not val.isdigit():
            break
    set_setting(constants.UID, val)
    return val


def showSettingsGui():
    xbmcaddon.Addon().openSettings()


def showGuiNotification(message):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (NAME, message, 5000, ICON))


def configCheck():
    if not get_setting_bool(constants.CONFIGURED):
        set_setting_bool(constants.CONFIGURED, True)
        showSettingsGui()
        return

def logout():
    utils.log("Clearing token")
    set_setting_bool(constants.LOGGED_IN, False)
    set_setting(constants.TOKEN, "")
    showGuiNotification("Authorization token cleared")
