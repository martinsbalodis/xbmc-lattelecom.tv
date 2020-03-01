import sys
import textwrap
import traceback
import urllib
import datetime
import time
import _strptime

import pytz
riga = pytz.timezone('Europe/Riga')

import config
import pyperclip

import xbmc
import xbmcplugin
import xbmcaddon


DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def log(s):
    xbmc.log("[%s v%s] %s" % (config.NAME, config.VERSION, s), level=xbmc.LOGNOTICE)


def log_error(message=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if message:
        exc_value = message
    xbmc.log("[%s v%s] ERROR: %s (%d) - %s" % (
        config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value),
             level=xbmc.LOGNOTICE)
    traceback.print_exc()


def dialog_error(msg):
    # Generate a list of lines for use in XBMC dialog
    content = []
    exc_type, exc_value, exc_traceback = sys.exc_info()
    content.append("%s v%s Error" % (config.NAME, config.VERSION))
    content.append("%s (%d) - %s" % (exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, msg))
    content.append(str(exc_value))
    return content


def dialog_message(msg, title=None):
    if not title:
        title = "%s v%s" % (config.NAME, config.VERSION)
    # Add title to the first pos of the textwrap list
    content = textwrap.wrap(msg, 60)
    content.insert(0, title)
    return content


def get_url(s):
    dict = {}
    pairs = s.lstrip("?").split("&")
    for pair in pairs:
        if len(pair) < 3: continue
        kv = pair.split("=", 1)
        k = kv[0]
        v = urllib.unquote_plus(kv[1])
        dict[k] = v
    return dict


def isEmpty(param):
    if param is None or param == "":
        return True

def dateLocatToUtc(date):
    local_dt = riga.localize(date, is_dst=None)
    return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

def dateTounixTS(date):
    return int((date - datetime.datetime(1970,1,1)).total_seconds())

def dateTounixUtcTS(date):
    return dateTounixTS(dateLocatToUtc(date))

def dateFromString(string, fmt=DATE_FORMAT):
    # Workaround from https://forum.kodi.tv/showthread.php?tid=112916
    try:
        res = datetime.datetime.strptime(string, fmt)
    except TypeError:
        res = datetime.datetime(*(time.strptime(string, fmt)[0:6]))
    return res

def dateFromUnix(string):
    return datetime.datetime.utcfromtimestamp(string)

def unixTSFromDateString(string):
    dt=datetime.datetime(*(time.strptime(string, "%Y-%m-%d")[:6]))
    return dateTounixTS(dt)

def stringFromDateNow():
    return datetime.datetime.now().strftime(DATE_FORMAT)


def set_content(content):
    xbmcplugin.setContent(int(sys.argv[1]), content)

def set_view(content):
    if content:
        set_content(content)
    view = config.get_setting('%s_view' % content)
    if view and view != '0':
        xbmc.executebuiltin('Container.SetViewMode(%s)' % view)

def color_str(color, string):
    return '[COLOR'+ color + ']' + string + '[/COLOR]'

def color_str_yellow(string): return color_str('yellow', string)
def color_str_pink(string): return color_str('pink', string)
def color_str_orange(string): return color_str('orange', string)
def color_str_greenyellow(string): return color_str('greenyellow', string)


def copy_to_clipboard(string): pyperclip.copy(string)
