import sys

from lib import utils, channels, config, constants, epg

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
        channels.make_channel_list()
    elif params.has_key("play"):
        channels.play_channel()
    else:
        utils.log("Unknown url: " + sys.argv[0])
