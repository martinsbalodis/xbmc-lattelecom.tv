import json
import urllib
import urllib2
import time
import datetime

import config
import utils
import constants
import cache

from exceptions import ApiError

try:
    import xbmc, xbmcplugin
except:
    pass

API_BASEURL = "https://manstv.lattelecom.tv"
API_ENDPOINT = API_BASEURL + "/api/v1.7"
USER_AGENT = 'Shortcut.lv for Android TV v1.11.9 / Dalvik/2.1.0 (Linux; U; Android 7.1.1; sdk_google_atv_x86 Build/NYC)'


def get_url_opener(referrer=None):
    opener = urllib2.build_opener()
    # Headers from Nexus 6P
    opener.addheaders = [
        ('User-Agent', USER_AGENT),
        ('Connection', 'keep-alive'),
    ]
    return opener


def login_check():
    utils.log("login_check: LAST_LOGIN: " + config.X.LAST_LOGIN)
    
    if utils.isEmpty(config.X.USERNAME) or utils.isEmpty(config.X.PASSWORD):
        config.X.LOGGED_IN = False
        config.X.TOKEN = ""
        config.showSettingsGui()
        return
        
    # Periodically (1 day) force update token because it can expire
    update = not config.X.LOGGED_IN or utils.isEmpty(config.X.TOKEN)
    update = update or utils.isEmpty(config.X.LAST_LOGIN)
    if not update:
        t1 = utils.dateFromString(config.X.LAST_LOGIN)
        t2 = datetime.datetime.now()
        interval = 1
        update = abs(t2 - t1) > datetime.timedelta(days=interval)
    if update is True:
        utils.log("Refreshing Lattelecom login token")
        try:
            login(force=True)
        except ApiError as e:
            config.showGuiNotification(str(e))
            utils.log(str(e))
    else:
        utils.log("Lattelecom login token seems quite fresh.")


def login(force=False):
    utils.log("login for User: " + config.X.USERNAME + "; Logged in: " + str(config.X.LOGGED_IN) + "; Token: " + config.X.TOKEN)

    if force is False and not utils.isEmpty(config.X.TOKEN) and config.X.LOGGED_IN:
        utils.log("Already logged in")
        return True

    config.X.LOGGED_IN = False
    config.X.TOKEN = ""

    values = {'id': config.X.USERNAME,
              'uid': config.get_unique_id(),
              'password': config.X.PASSWORD}
    if utils.isEmpty(values['id']): return False

    opener = get_url_opener()
    response = opener.open(API_ENDPOINT + '/post/user/users', urllib.urlencode(values))

    response_code = response.getcode()
    response_text = response.read()

    if response_code == 422:
        raise ApiError("Login failed, Status: 422 Unprocessable Entity. Did you enter username/password?")

    if response_code == 401:
        raise ApiError("Login failed, Status: 401 unauthorized. Check your username/password")

    if response_code != 200:
        raise ApiError(
            "Got incorrect response code during login. Reponse code: " + response_code + "; Text: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        utils.log("Did not receive json, something wrong: " + response_text)
        raise ApiError("Failed to log in, API error")

    utils.log(response_text)

    config.X.TOKEN = json_object["data"]["attributes"]["token"]
    config.X.LOGGED_IN = True
    config.X.LAST_LOGIN = utils.stringFromDateNow()

    config.showGuiNotification("Login successful")
    utils.log("Login success! Token: " + config.X.TOKEN)
    return True


@cache.cache_function(cache_limit=240)
def get_channels():
    utils.log("get_channels")

    url = API_ENDPOINT + '/get/content/packages?include=channels'
    opener = get_url_opener()
    response = opener.open(url)
    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        raise ApiError(
            "Got incorrect response code while requesting channel list. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        raise ApiError("Did not receive json, something wrong: " + response_text)

    if "included" not in json_object:
        raise ApiError("Invalid response: " + response_text)

    channels = []
    for item in json_object["included"]:
        if "type" not in item or "id" not in item:
            continue

        if item["type"] != "channels":
            continue

        if item["attributes"] is None or item["attributes"]["title"] is None:
            continue

        channels.append({
            'id': item["id"],
            'name': item["attributes"]["title"],
            'logo': item["attributes"]["logo-url"],
            'thumb': item["attributes"]["epg-default-poster-url"]
        })
    
    return channels


@cache.cache_function(cache_limit=3)
def get_stream_url(data_url):
    utils.log("get_stream_url for channel: " + data_url + " quality: " + config.X.QUALITYX)
    login_check()

    streamurl = None

    url = API_ENDPOINT + "/get/content/live-streams/" + data_url + "?include=quality"
    opener = get_url_opener()
    opener.addheaders.append(('Authorization', "Bearer " + config.X.TOKEN))
    response = opener.open(url)

    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        config.X.LOGGED_IN = False
        raise ApiError(
            "Got incorrect response code while requesting stream info. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.X.LOGGED_IN = False
        raise ApiError("Did not receive json, something wrong: " + response_text)

    stream_links = {}

    for stream in json_object["data"]:

        if stream["type"] != "live-streams":
            continue

        url = stream["attributes"]["stream-url"]

        if "_lq.stream" in stream["id"]:
            stream_links["3-lq"] = url
        elif "_mq.stream" in stream["id"]:
            stream_links["2-mq"] = url
        elif "_hq.stream" in stream["id"]:
            stream_links["1-hq"] = url
        elif "_hd.stream" in stream["id"]:
            stream_links["0-hd"] = url
    
    quality = config.X.QUALITYX

    for key in sorted(stream_links.keys()):
        if key >= quality:
            streamurl = stream_links[key]
            break
        streamurl = stream_links[key]

    return streamurl


@cache.cache_function(cache_limit=3)
def get_archive_url(eventid):
    utils.log("get_archive_url for event: " + eventid)
    login_check()

    streamurl = None

    url = API_ENDPOINT + "/get/content/record-streams/" + eventid + "?include=quality"
    opener = get_url_opener()
    opener.addheaders.append(('Authorization', "Bearer " + config.X.TOKEN))
    response = opener.open(url)

    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        config.X.LOGGED_IN = False
        raise ApiError(
            "Got incorrect response code while requesting stream info. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.X.LOGGED_IN = False
        raise ApiError("Did not receive json, something wrong: " + response_text)

    stream_links = {}

    for stream in json_object["data"]:

        if stream["type"] != "record-streams":
            continue

        url = stream["attributes"]["stream-url"]

        if "_lq." in stream["id"]:
            stream_links["3-lq"] = url
        elif "_mq." in stream["id"]:
            stream_links["2-mq"] = url
        elif "_hq." in stream["id"]:
            stream_links["1-hq"] = url
        elif "_hd." in stream["id"]:
            stream_links["0-hd"] = url

    quality = config.X.QUALITYX

    for key in sorted(stream_links.keys()):
        if key >= quality:
            streamurl = stream_links[key]
            break
        streamurl = stream_links[key]

    return streamurl


@cache.cache_function(cache_limit=192)
def get_epg_a(date_from, date_to, chid = ''):
    utils.log("get_epg_a: [%s]-[%s] [%s]" %(str(date_from), str(date_to), chid))

    timestampFrom = utils.dateTounixUtcTS(date_from)
    timestampTo = utils.dateTounixUtcTS(date_to)

    url = API_ENDPOINT + "/get/content/epgs/?include=channel&page[size]=100000&filter[utTo]="+str(timestampTo)+"&filter[utFrom]="+str(timestampFrom)
    if chid != '' and not chid is None:
        url = url + "&filter[channel]=" + str(chid)
        
    opener = get_url_opener()
    response = opener.open(url)
    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        raise ApiError("Got bad response from EPG service. Response code: " + response_code)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        raise ApiError("Did not receive json, something wrong: " + response_text)

    return json_object


def get_epg(datestr):
    utils.log("get_epg date: " + str(datestr))
    date = utils.dateFromString(datestr, "%Y-%m-%d")
    dateto = date + datetime.timedelta(seconds=86400)
    return get_epg_a(date, dateto)


def get_epg_for_channel(date, chid):
    utils.log("get_epg_for_channel " + str(date) + " " + chid)
    dateto = date + datetime.timedelta(seconds=86400)
    return get_epg_a(date, dateto, chid)


def get_epg_now():
    utils.log("get_epg_now")
    dateutc = datetime.datetime.utcfromtimestamp(time.time())
    return get_epg_a(dateutc, dateutc)


def prepare_epg(epg_data, bychannel=True):
    utils.log("prepare_epg")
    events = {}
    for item in epg_data["data"]:
        if item["type"] != "epgs":
            continue
        id = item["id"]
        chid = item["relationships"]["channel"]["data"]["id"]
        time_start = utils.dateFromUnix(float(item["attributes"]["unix-start"]))
        time_stop = utils.dateFromUnix(float(item["attributes"]["unix-stop"]))
        time_start = utils.dateFromUtcToLocal(time_start)
        time_stop = utils.dateFromUtcToLocal(time_stop)
        title = item["attributes"]["title"]
        desc = item["attributes"]["description"]
        
        event = {}
        event["id"] = id
        event["chid"] = chid
        event["start"] = time_start
        event["stop"] = time_stop
        event["title"] = title.encode('utf8')
        event["desc"] = desc.encode('utf8')
        event["poster"] = API_BASEURL + '/' + item["attributes"]["poster-url"]

        if bychannel:
            events[chid] = event
        else:
            events[id] = event

    return events


def filter_pepg(pepg = {}, bychid = False, filterchannel = '', 
                filtertimefrom = None, filtertimeto = None):
    events = {}
    for key, val in pepg.items():
        chid = val['chid']
        time_start = val['start']
        time_stop = val['stop']
        if not utils.isEmpty(filterchannel) and chid != filterchannel: 
            continue
        if not filtertimefrom is None and not filtertimeto is None:
            if time_start > filtertimeto or time_stop < filtertimefrom:
                continue
        if bychid:
            events[chid] = val
        else:
            events[key] = val
    return events


def prepare_epg_now():
    utils.log("prepare_epg_now")
    date_now = datetime.datetime.fromtimestamp(time.time())
    date_today = utils.dateToDateTime(datetime.date.today())
    sdate = date_today.strftime('%Y-%m-%d')
    epg_data = get_epg_for_channel(date_today, '')
    if epg_data is None: return {}
    pepg = prepare_epg(epg_data, False)
    pepg = filter_pepg(pepg, True, '', date_now, date_now)
    return pepg
        
        
def prepare_epg_for_channel(date, chid):
    utils.log("prepare_epg_for_channel")
    dateto = date + datetime.timedelta(seconds=86400)
    sts, epg_data = cache._get_func('get_epg_a',(date, dateto, ''), {}, 192)
    if sts:
        pepg = prepare_epg(epg_data, False)
        return filter_pepg(pepg, False, chid)
    else:
        epg_data = get_epg_for_channel(date, chid)
        return prepare_epg(epg_data, False)
