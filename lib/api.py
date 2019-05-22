import json
import urllib
import urllib2
import config
import utils
import constants

from exceptions import ApiError

try:
    import xbmc, xbmcplugin
except:
    pass

API_ENDPOINT = "https://manstv.lattelecom.tv"


def get_url_opener(referrer=None):
    opener = urllib2.build_opener()
    # Headers from Nexus 6P
    opener.addheaders = [
        ('User-Agent',
         'Shortcut.lv for Android TV v1.11.9 / Dalvik/2.1.0 (Linux; U; Android 7.1.1; sdk_google_atv_x86 Build/NYC)'),
        ('Connection', 'keep-alive'),
    ]
    return opener


def login(force=False):
    utils.log("User: " + config.get_setting(constants.USERNAME) + "; Logged in: " + str(config.get_setting_bool(
        constants.LOGGED_IN)) + "; Token: " + config.get_setting(constants.TOKEN))

    if force is False and not utils.isEmpty(config.get_setting(constants.TOKEN)) and config.get_setting_bool(constants.LOGGED_IN):
        utils.log("Already logged in")
        return

    opener = get_url_opener()

    values = {'username': config.get_setting(constants.USERNAME),
              'uid': config.get_unique_id(),
              'password': config.get_setting(constants.PASSWORD)}

    response = opener.open(API_ENDPOINT + '/api/v1.4/post/user/login', urllib.urlencode(values))

    response_code = response.getcode()
    response_text = response.read()

    if response_code != 200:
        raise ApiError(
            "Got incorrect response code during login. Reponse code: " + response_code + "; Text: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.set_setting_bool(constants.LOGGED_IN, False)
        config.set_setting(constants.TOKEN, "")
        utils.log("Did not receive json, something wrong: " + response_text)
        raise ApiError("Failed to log in, API error")

    if json_object["status"] == "ko":
        config.set_setting_bool(constants.LOGGED_IN, False)
        config.set_setting(constants.TOKEN, "")

        utils.log("Failed to log in. Message: " + response_text)
        raise ApiError("Failed to log in, check credentials")

    utils.log(response_text)

    config.set_setting_bool(constants.LOGGED_IN, True)
    config.set_setting(constants.TOKEN, json_object["token"])

    utils.log("Login success! Token: " + config.get_setting(constants.TOKEN))
    return True


def get_channels():
    config.login_check()

    url = API_ENDPOINT + '/api/v1.4/get/tv/channels'
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

    if json_object["status"] != "ok":
        raise ApiError("Invalid response: " + response_text)

    channels = []
    for item in json_object['items']:

        if item["name"] is None:
            continue

        if item["live"] == "0":
            continue

        if item["streaming_url"] == "":
            continue

        channels.append({
            'id': item["id"],
            'name': item["name"],
            'logo': item["logo"],
            'lang': item["lang"],
            'thumb': item["broadcast_default_picture"],
            'streaming_url': item["streaming_url"]
        })

    return channels


def get_stream_url(data_url):
    utils.log("Getting URL for channel: " + data_url)
    config.login_check()

    streamurl = None

    url = API_ENDPOINT + "/api/v1.7/get/content/live-streams/" + data_url + "?include=quality"
    opener = get_url_opener()
    opener.addheaders.append(('Authorization', "Bearer " + config.get_setting(constants.TOKEN)))
    response = opener.open(url)

    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        config.set_setting_bool(constants.LOGGED_IN, False)
        raise ApiError(
            "Got incorrect response code while requesting stream info. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.set_setting(constants.LOGGED_IN, False)
        raise ApiError("Did not receive json, something wrong: " + response_text)

    stream_links = {}

    for stream in json_object["data"]:

        if stream["type"] != "live-streams":
            continue

        url = stream["attributes"]["stream-url"] + "&auth_token=app_" + config.get_setting(constants.TOKEN)

        if "_lq.stream" in stream["id"]:
            stream_links["3-lq"] = url
        elif "_mq.stream" in stream["id"]:
            stream_links["2-mq"] = url
        elif "_hq.stream" in stream["id"]:
            stream_links["1-hq"] = url
        elif "_hd.stream" in stream["id"]:
            stream_links["0-hd"] = url

    for key in sorted(stream_links.keys()):
        streamurl = stream_links[key]
        break

    return streamurl


def get_epg(date):
    utils.log("Getting EPG for date: " + date)
    config.login_check()

    url = API_ENDPOINT + "/api/v1.4/get/tv/epg/?daynight=" + date
    opener = get_url_opener()
    opener.addheaders.append(('Authorization', "Bearer " + config.get_setting(constants.TOKEN)))
    response = opener.open(url)

    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        config.set_setting_bool(constants.LOGGED_IN, False)
        raise ApiError(
            "Got bad response from EPG service. Response code: " + response_code)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.set_setting(constants.LOGGED_IN, False)
        raise ApiError("Did not receive json, something wrong: " + response_text)

    return json_object
