import sys
import textwrap
import traceback
import urllib

import config


def log(s):
    print "[%s v%s] %s" % (config.NAME, config.VERSION, s)


def log_error(message=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if message:
        exc_value = message
    print "[%s v%s] ERROR: %s (%d) - %s" % (
    config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value)
    print traceback.print_exc()


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
