from lib import config
if not config.X.SERVICE_ENABLED: exit()

import xbmc
from lib import api, utils, exceptions, epg

utils.log("Service started")

if __name__ == '__main__':
    monitor = xbmc.Monitor()

    config.configCheck()

    # Force login token refresh upon Kodi start
    try:
        api.login(force=True)
    except exceptions.ApiError as e:
        config.showGuiNotification(str(e))
        utils.log(str(e))
        pass

    while not monitor.abortRequested():

        if epg.should_update():
            epg.build_epg()

        if monitor.waitForAbort(10):
            break
