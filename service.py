from lib import config
if not config.X.SERVICE_ENABLED: exit()

import xbmc
from lib import api, utils, exceptions, epg

utils.log("Service started")

if __name__ == '__main__':
    monitor = xbmc.Monitor()

    config.configCheck()

    while not monitor.abortRequested():

        if epg.should_update():
            epg.build_epg()

        if monitor.waitForAbort(10):
            break
