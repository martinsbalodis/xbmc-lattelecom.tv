# -*- coding: utf-8 -*-
import sys
import datetime
import urllib

import xbmcgui
import xbmcplugin

import api
import utils

def make_main_menu():
    utils.log("make_main_menu " + sys.argv[0])
    utils.set_view('files')

    listitem = xbmcgui.ListItem(label=u'Tiešreide'.encode('utf-8'))
    listitem.setProperty('IsPlayable', "false")
    url = "%s?mode=livechannels" % (sys.argv[0])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

    listitem = xbmcgui.ListItem(label=u'Arhīvs'.encode('utf-8'))
    listitem.setProperty('IsPlayable', "false")
    url = "%s?mode=archivechannels" % (sys.argv[0])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def make_channel_list():
    utils.log("make_channel_list " + sys.argv[0])
    utils.set_view('videos')

    REFRESH = 'special://home/addons/lattelecomtv/lib/refresh.py'
    REFRESH_CMD = 'RunScript(%s)' % REFRESH

    try:
        channels = api.get_channels()
        epgnow = api.prepare_epg_now()

        ok = True
        for c in channels:
            event = epgnow[c['id']]
            name = c['name'].encode('utf8')
            name = utils.color_str_yellow(name)
            start = event['start'].strftime('%H:%M')
            stop = event['stop'].strftime('%H:%M')
            time = start + '-' + stop
            time = utils.color_str_greenyellow(time)
            label = '{} - {} - {}'.format(name, time, event['title'])
            desc = label + '\n' + event['desc']

            listitem = xbmcgui.ListItem(label=label)
            listitem.setInfo('video', {'title': label, 'plot':desc})
            listitem.setArt({'icon':api.API_BASEURL + "/" + c['logo'],
                             'thumb':api.API_BASEURL + "/" + c['thumb']})
            listitem.setProperty('IsPlayable', "true")

            # Build the URL for the program, including the list_info
            url = "%s?mode=play&chid=%s" % (sys.argv[0], c['id'])
            archive_url = "%s?mode=gotoarchive&chid=%s" % (sys.argv[0], c['id'])
            
            contextMenuItems = []
            contextMenuItems.append(('Refresh', REFRESH_CMD))
            contextMenuItems.append(('Archive', 'Container.Update(' + archive_url + ')'))
            listitem.addContextMenuItems(contextMenuItems, replaceItems=False)

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok, updateListing=True, cacheToDisc=False)
        
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def make_archive_channel_list():
    utils.log("make_archive_channel_list " + sys.argv[0])
    utils.set_view('files')

    try:
        channels = api.get_channels()
 
        ok = True
        for c in channels:
            name = c['name'].encode('utf8')
            name = utils.color_str_yellow(name)
            name = name + u' (arhīvs)'.encode('utf8')

            listitem = xbmcgui.ListItem(label=name)
            listitem.setArt({'icon':api.API_BASEURL + "/" + c['logo'],
                             'thumb':api.API_BASEURL + "/" + c['thumb']})
            listitem.setProperty('IsPlayable', "false")

            url = "%s?mode=gotoarchive&chid=%s" % (sys.argv[0], c['id'])
            
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, 
                                             listitem=listitem, 
                                             isFolder=True,
                                             totalItems=len(channels))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def make_channel_date_list(chid):
    utils.log("make_channel_date_list " + sys.argv[0])
    utils.set_view('files')
    try:
        ok = True
        dt = datetime.date.today()
        for i in range(7):
            dt2 = dt + datetime.timedelta(days=-i)
            sdt = dt2.strftime('%A %d. %B')
            urldt = dt2.strftime('%Y%m%d')
            listitem = xbmcgui.ListItem(label=sdt)
            listitem.setProperty('IsPlayable', "false")
            url = "%s?mode=getarchive&date=%s&chid=%s" % (sys.argv[0], urldt, chid)
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def make_channel_event_list(chid, date):
    utils.log("make_channel_event_list " + sys.argv[0])
    utils.set_view('videos')

    try:
        epg = api.prepare_epg_for_channel(date, chid)
        ok = True
        for event in sorted(epg.values(), key = lambda x: x['start']):
            start = event['start'].strftime('%H:%M')
            stop = event['stop'].strftime('%H:%M')
            time = start
            time = utils.color_str_greenyellow(time)
            time2 = start + '-' + stop
            time2 = utils.color_str_greenyellow(time2)
            label = '{} - {}'.format(time, event['title'])
            desc = '{} - {}\n{}'.format(time2, event['title'], event['desc'])
            start2 = event['start'].strftime('%d %b')
            title = start2 + ' ' + event['title']

            listitem = xbmcgui.ListItem(label=label)
            listitem.setInfo('video', {'title': title, 'plot':desc})
            listitem.setArt({'poster':event['poster']})
            listitem.setProperty('IsPlayable', "true")
            
            contextMenuItems = []
            cm_url = "%s?mode=copyarchivelink&eventid=%s" % (sys.argv[0], event['id'])
            contextMenuItems.append(('Copy Link to Clipboard', 'RunPlugin(' + cm_url + ')'))
            listitem.addContextMenuItems(contextMenuItems, replaceItems=False)

            url = "%s?mode=playarchive&eventid=%s" % (sys.argv[0], event['id'])

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def play_channel(chid):
    utils.log("url play channel: " + sys.argv[0])
    user_agent_x = 'User-Agent=' + urllib.quote_plus(api.USER_AGENT)

    try:
        handle = int(sys.argv[1])
        rtmp_url = api.get_stream_url(chid)

        playitem = xbmcgui.ListItem(path=rtmp_url)
        playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        playitem.setProperty('inputstream.adaptive.stream_headers', user_agent_x)
        playitem.setContentLookup(False)
        xbmcplugin.setResolvedUrl(handle, True, playitem)
       
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def play_archive(eventid):
    utils.log("url play archive: " + sys.argv[0])
    user_agent_x = 'User-Agent=' + urllib.quote_plus(api.USER_AGENT)

    try:
        handle = int(sys.argv[1])
        rtmp_url = api.get_archive_url(eventid)

        playitem = xbmcgui.ListItem(path=rtmp_url)
        playitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        playitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        playitem.setProperty('inputstream.adaptive.stream_headers', user_agent_x)
        playitem.setContentLookup(False)
        xbmcplugin.setResolvedUrl(handle, True, playitem)

    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch listing")
        d.ok(*msg)
        utils.log_error()


def copy_archive_url(eventid):
    utils.log("copy_archive_url: " + sys.argv[0])
    user_agent_x = 'User-Agent=' + urllib.quote_plus(api.USER_AGENT)
    try:
        handle = int(sys.argv[1])
        rtmp_url = api.get_archive_url(eventid)
        utils.copy_to_clipboard(rtmp_url)
        utils.notify(msg='Done!')
    except:
        d = xbmcgui.Dialog()
        msg = utils.dialog_error("Unable to fetch url")
        d.ok(*msg)
        utils.log_error()

