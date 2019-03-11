import sys

from lib import utils, channels

utils.log('Initialised')

if __name__ == "__main__":
    utils.log("got URL: " + sys.argv[0] + sys.argv[1] + sys.argv[2])

    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if (len(params) == 0):
        channels.make_channel_list()
    elif params.has_key("play"):
        channels.play_channel()
    else:
        utils.log("Unknown url: " + sys.argv[0])
