import os
import sys
import cookielib

try:
    import xbmcplugin, xbmc
except:
    pass

NAME = 'ABC iView'
VERSION = '0.0.1'

api_version = 383

# os.uname() is not available on Windows, so we make this optional.
try:
    uname = os.uname()
    os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
    os_string = ''

user_agent = '%s plugin for XBMC %s%s' % (NAME, VERSION, os_string)

base_url   = 'http://www.abc.net.au/iview/'
config_url = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
auth_url   = 'http://tviview.abc.net.au/iview/auth/?v2'
series_url = 'http://www.abc.net.au/iview/api/series_mrss.htm?id=%s'

akamai_fallback_server = 'rtmp://cp53909.edgefcs.net/ondemand'
akamai_playpath_prefix = 'flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = '96cc76f1d5385fb5cda6e2ce5c73323a399043d0bb6c687edd807e5c73c42b37'
swf_size    = '2122'
swf_url     = 'http://www.abc.net.au/iview/images/iview.jpg'

def get_config(key):
    addon_handle = int(sys.argv[1])
    return xbmcplugin.getSetting(addon_handle, key)

def set_config(key, value):
    addon_handle = int(sys.argv[1])
    return xbmcplugin.setSetting(addon_handle, key, value)

def get_cookiejar_file():
    cookiejar_file = xbmc.translatePath("special://home/addons/lattelecomtv/resources/cookie.dat")
    return cookiejar_file

def get_cookiejar():
    cookiejar_file = get_cookiejar_file()
    cookiejar = cookielib.LWPCookieJar()
    if os.path.exists(cookiejar_file):
        cookiejar.load(filename=cookiejar_file, ignore_discard=True)
    return cookiejar

def delete_cookiejar():
    cookiejar_file = get_cookiejar_file()
    try:
        os.remove(cookiejar_file)
    except:
        pass