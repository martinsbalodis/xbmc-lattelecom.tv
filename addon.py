import os
import sys

# Add our resources/lib to the python path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except:
    current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, 'resources', 'lib'))

import utils, channels

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
