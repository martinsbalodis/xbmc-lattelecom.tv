import json
import urllib
import urllib2
import config
import utils
import constants
import time
import datetime

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

    if not config.X.LOGGED_IN:
        # Ask for credentials if they are missing
        if utils.isEmpty(config.X.USERNAME) or utils.isEmpty(config.X.PASSWORD):
            config.showSettingsGui()
            return
        # Log in and show a status notification
        try:
            login()
            config.showGuiNotification("Login successful")
        except ApiError as e:
            config.showGuiNotification(str(e))
            utils.log(str(e))
            pass
        return

    # Periodically (1 day) force update token because it can expire
    update = False
    if utils.isEmpty(config.X.LAST_LOGIN):
        update = True
    else:
        t1 = utils.dateFromString(config.X.LAST_LOGIN)
        t2 = datetime.datetime.now()
        interval = 1
        update = abs(t2 - t1) > datetime.timedelta(days=interval)
    if update is True:
        utils.log("Refreshing Lattelecom login token")
        config.X.LAST_LOGIN = utils.stringFromDateNow()
        try:
            login(force=True)
        except ApiError as e:
            config.showGuiNotification(str(e))
            utils.log(str(e))
            pass
    else:
        utils.log("Lattelecom login token seems quite fresh.")


def login(force=False):
    utils.log("User: " + config.X.USERNAME + "; Logged in: " + str(config.X.LOGGED_IN) + "; Token: " + config.X.TOKEN)

    if force is False and not utils.isEmpty(config.X.TOKEN) and config.X.LOGGED_IN:
        utils.log("Already logged in")
        return

    opener = get_url_opener()

    values = {'id': config.X.USERNAME,
              'uid': config.get_unique_id(),
              'password': config.X.PASSWORD}
    if values['id'] is None or values['id'] == '': return False

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
        config.X.LOGGED_IN = False
        config.X.TOKEN = ""
        utils.log("Did not receive json, something wrong: " + response_text)
        raise ApiError("Failed to log in, API error")

    utils.log(response_text)

    config.X.LOGGED_IN = True
    config.X.TOKEN = json_object["data"]["attributes"]["token"]

    utils.log("Login success! Token: " + config.X.TOKEN)
    return True


def get_channels():
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


def get_stream_url(data_url):
    utils.log("Getting URL for channel: " + data_url + " quality: " + config.X.QUALITYX)
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

def get_archive_url(eventid):
    utils.log("Getting URL for event: " + eventid)
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

def get_epg(date):
    utils.log("Getting EPG for date: " + date)

    timestampFrom = utils.unixTSFromDateString(date)
    timestampTo=int(timestampFrom+86400)

    url = API_ENDPOINT + "/get/content/epgs/?include=channel&page[size]=100000&filter[utTo]="+str(timestampTo)+"&filter[utFrom]="+str(timestampFrom)
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

def get_epg_for_channel(date, chid):
    utils.log("Getting EPG for date " + date.strftime('%Y-%m-%d'))

    timestampFrom = utils.dateTounixUtcTS(date)
    timestampTo=int(timestampFrom+86400)

    url = API_ENDPOINT + "/get/content/epgs/?include=channel&page[size]=100000&filter[channel]=" + str(chid) + "&filter[utTo]="+str(timestampTo)+"&filter[utFrom]="+str(timestampFrom)
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

def get_epg_now():
    utils.log("Getting EPG for now playing")

    timestamp = int(time.time())

    url = API_ENDPOINT + "/get/content/epgs/?include=channel&page[size]=100000&filter[utTo]="+str(timestamp)+"&filter[utFrom]="+str(timestamp)
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


def prepare_epg(epg_data, bychannel=True):
    utils.log("Preparing EPG now")
    events = {}
    for item in epg_data["data"]:
        if item["type"] != "epgs":
            continue
        id = item["id"]
        chid = item["relationships"]["channel"]["data"]["id"]
        time_start = utils.dateFromUnix(float(item["attributes"]["unix-start"]))
        time_stop = utils.dateFromUnix(float(item["attributes"]["unix-stop"]))
        time_start = utils.riga.fromutc(time_start)
        time_stop = utils.riga.fromutc(time_stop)
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

def prepare_epg_now():
    epg_data = get_epg_now()
    return prepare_epg(epg_data, True)

def prepare_epg_for_channel(date, chid):
    utils.log("Preparing EPG for channel")
    epg_data = get_epg_for_channel(date, chid)
    return prepare_epg(epg_data, False)
