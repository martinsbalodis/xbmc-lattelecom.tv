import sys
import utils
import api

try:
    import xbmc, xbmcgui, xbmcplugin
except ImportError:
    pass # for PC debugging

def make_channel_list():

    utils.log("url-make-channel"+sys.argv[0])

    try:

        channels = api.get_channels()

        ok = True
        for c in channels:

            listitem = xbmcgui.ListItem(label=c['channel'])
            listitem.setInfo('video', { 'title': c['channel-info'] })

            ## Build the URL for the program, including the list_info
            url = "%s?play=true&data_url=%s" % (sys.argv[0], c['data-url'])

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False, totalItems=len(channels))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()

def play_channel():

    utils.log("url play channel: "+sys.argv[0])

    try:

        #iview_config = comm.get_config()
        #auth = comm.get_auth(iview_config)
        #
        ## We don't support Adobe HDS yet, Fallback to RTMP streaming server
        #if auth['rtmp_url'].startswith('http://'):
        #    auth['rtmp_url'] = iview_config['rtmp_url'] or config.akamai_fallback_server
        #    auth['playpath_prefix'] = config.akamai_playpath_prefix
        #    utils.log("Adobe HDS Not Supported, using fallback server %s" % auth['rtmp_url'])
        #
        #p = classes.Program()
        #p.parse_xbmc_url(url)
        #
        ## Playpath shoud look like this:
        ##   Akamai: mp4:flash/playback/_definst_/itcrowd_10_03_02
        #playpath = auth['playpath_prefix'] + p.url
        #if playpath.split('.')[-1] == 'mp4':
        #    playpath = 'mp4:' + playpath
        #
        ## Strip off the .flv or .mp4
        #playpath = playpath.split('.')[0]

        ## rtmp://cp53909.edgefcs.net/ondemand?auth=daEbjbeaCbGcgb6bedYacdWcsdXc7cWbDda-bmt0Pk-8-slp_zFtpL&aifp=v001
        ## playpath=mp4:flash/playback/_definst_/kids/astroboy_10_01_22 swfurl=http://www.abc.net.au/iview/images/iview.jpg swfvfy=true
        #rtmp_url = "%s?auth=%s playpath=%s swfurl=%s swfvfy=true" % (auth['rtmp_url'], auth['token'], playpath, config.swf_url)

        params_str = sys.argv[2]
        params = utils.get_url(params_str)
        # data_stream_url = params['data_stream_url']
        data_url = params['data_url']
        rtmp_url = api.get_stream_url(data_url)

        listitem=xbmcgui.ListItem(label="video")
        #listitem.setInfo('video', p.get_xbmc_list_item())

        #if hasattr(listitem, 'addStreamInfo'):
        #    listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
        #    listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

        xbmc.Player().play(rtmp_url, listitem)
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()