import sys
import textwrap
import traceback
import urllib
import xbmc
import datetime
import time

import config

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


def dateFromString(string):
    # Workaround from https://forum.kodi.tv/showthread.php?tid=112916
    fmt = DATE_FORMAT
    try:
        res = datetime.datetime.strptime(string, fmt)
    except TypeError:
        res = datetime.datetime(*(time.strptime(string, fmt)[0:6]))
    return res


def stringFromDateNow():
    return datetime.datetime.now().strftime(DATE_FORMAT)
