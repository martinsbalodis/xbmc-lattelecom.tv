import datetime
import os
import random
import sys

import xbmc
import xbmcaddon
import xbmcplugin

import api
import constants
import utils
from exceptions import ApiError

ADDON = xbmcaddon.Addon()
APPID = xbmcaddon.Addon().getAddonInfo("id")
NAME = xbmcaddon.Addon().getAddonInfo("name")
VERSION = xbmcaddon.Addon().getAddonInfo("version")
ICON = xbmcaddon.Addon().getAddonInfo("icon")

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


def login_check():
    if not get_setting_bool(constants.LOGGED_IN):
        # Ask for credentials if they are missing
        if utils.isEmpty(get_setting(constants.USERNAME)) or utils.isEmpty(get_setting(constants.PASSWORD)):
            showSettingsGui()
            return
        # Log in and show a status notification
        try:
            api.login()
            showGuiNotification("Login successful")
        except ApiError as e:
            showGuiNotification(str(e))
            utils.log(str(e))
            pass
        return

    # Periodically (1 day) force update token because it can expire
    t1 = utils.dateFromString(get_setting(constants.LAST_LOGIN))
    t2 = datetime.datetime.now()
    interval = 1
    update = abs(t2 - t1) > datetime.timedelta(days=interval)
    if update is True:
        utils.log("Refreshing Lattelecom login token")
        set_setting(constants.LAST_LOGIN, utils.stringFromDateNow())
        try:
            api.login(force=True)
        except ApiError as e:
            showGuiNotification(str(e))
            utils.log(str(e))
            pass
    else:
        utils.log("Lattelecom login token seems quite fresh.")


def logout():
    utils.log("Clearing token")
    set_setting_bool(constants.LOGGED_IN, False)
    set_setting(constants.TOKEN, "")
    showGuiNotification("Authorization token cleared")
