import sys

import xbmcgui
import xbmcplugin

import api
import utils


def make_channel_list():
    utils.log("url-make-channel" + sys.argv[0])

    try:
        channels = api.get_channels()

        ok = True
        for c in channels:
            listitem = xbmcgui.ListItem(label=c['name'])
            listitem.setInfo('video', {'title': c['name']})
            listitem.setIconImage('https://manstv.lattelecom.tv/' + c['logo'])
            listitem.setThumbnailImage('https://manstv.lattelecom.tv/' + c['thumb'])
            listitem.setProperty('IsPlayable', "true")

            # Build the URL for the program, including the list_info
            url = "%s?play=true&data_url=%s" % (sys.argv[0], c['id'])

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False,
                                             totalItems=len(channels))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def play_channel():
    utils.log("url play channel: " + sys.argv[0])

    try:
        handle = int(sys.argv[1])
        params_str = sys.argv[2]
        params = utils.get_url(params_str)

        data_url = params['data_url']
        rtmp_url = api.get_stream_url(data_url)

        playitem = xbmcgui.ListItem(path=rtmp_url)
        playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        playitem.setContentLookup(False)
        xbmcplugin.setResolvedUrl(handle, True, playitem)

    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()

