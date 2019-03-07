import os
import random
import sys

try:
    import xbmcaddon, xbmcplugin, xbmc

    APPID = xbmcaddon.Addon().getAddonInfo("id")
    NAME = xbmcaddon.Addon().getAddonInfo("name")
    VERSION = xbmcaddon.Addon().getAddonInfo("version")
except:
    APPID = 'id'
    NAME = 'name'
    VERSION = 'version'
    pass

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


def get_setting(key):
    return xbmcaddon.Addon(APPID).getSetting(key)


def get_unique_id():
    if get_setting("uid") is not None and get_setting("uid") != "":
        return get_setting("uid")

    digits = '0123456789'
    letters = 'abcdef'
    all_chars = digits + letters
    length = 16
    val = None
    while True:
        val = ''.join(random.choice(all_chars) for i in range(length))
        if not val.isdigit():
            break
    set_setting("uid", val)
    return val
