import xbmc

from lib import api, config, utils, exceptions

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

        if monitor.waitForAbort(10):
            break
