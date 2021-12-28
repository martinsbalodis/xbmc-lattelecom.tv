import sys
from lib import utils, channels, config, constants, epg, cache
import xbmc

utils.log('Initialised')

if __name__ == "__main__":
    utils.log("got URL: " + "; ".join(sys.argv))

    if sys.argv[1] == constants.REFRESH_TOKEN:
        config.logout()
        exit(0)

    elif sys.argv[1] == constants.REBUILD_EPG:
        epg.build_epg()
        exit(0)

    elif sys.argv[1] == constants.CONFIGURE_EPG:
        epg.configure_epg()
        exit(0)

    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if len(params) == 0:
        #channels.make_main_menu()
        channels.make_channel_list()
    elif params.has_key("mode"):
        mode = params["mode"]
        if mode == "livechannels":
            channels.make_channel_list()
        elif mode == "archivechannels":
            channels.make_archive_channel_list()
        elif mode == "gotoarchive":
            chid = params["chid"]
            channels.make_channel_date_list(chid)
        elif mode == "getarchive":
            chid = params["chid"]
            sdt = params["date"]
            dt = utils.dateFromString(sdt, '%Y%m%d')
            channels.make_channel_event_list(chid, dt)
        elif mode == "play":
            chid = params["chid"]
            channels.play_channel(chid)
        elif mode == "playarchive":
            eventid = params["eventid"]
            channels.play_archive(eventid)
        elif mode == "copyarchivelink":
            eventid = params["eventid"]
            channels.copy_archive_url(eventid)
        elif mode == "reset_cache":
            cache.reset_cache()
    elif params.has_key("play"):
        chid = params["data_url"]
        channels.play_channel(chid)
    else:
        utils.log("Unknown url: " + sys.argv[0])
