import urllib, urllib2
import utils
import json

import config

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
         'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 6P Build/MTC19T)'),
        ('Connection', 'keep-alive'),
    ]
    return opener


def login():
    utils.log("User: " + config.get_config("username") + "; Logged in: " + config.get_setting(
        "logged_in") + "; Token: " + config.get_setting("token"))
    logged_in = config.get_setting("logged_in")
    if (config.get_setting("token") is not None and config.get_setting(
            "token") != "" and logged_in is not None and logged_in == "true"):
        utils.log("Already logged in")
        return

    opener = get_url_opener()

    values = {'username': config.get_config("username"),
              'uid': config.get_unique_id(),
              'password': config.get_config('password')}

    response = opener.open(API_ENDPOINT + '/api/v1.4/post/user/login', urllib.urlencode(values))

    response_code = response.getcode()
    response_text = response.read()

    if response_code != 200:
        raise Exception(
            "Got incorrect response code during login. Reponse code: " + response_code + "; Text: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        raise Exception("Did not receive json, something wrong: " + response_text)

    if json_object["status"] == "ko":
        raise Exception("Failed to log in. Probably wrong username and password. Message: " + response_text)

    utils.log(response_text)

    config.set_setting("logged_in", "true")
    config.set_setting("token", json_object["token"])

    utils.log("Login success! Token: " + config.get_setting("token"))


def get_channels():
    login()

    url = API_ENDPOINT + '/api/v1.4/get/tv/channels'
    opener = get_url_opener()
    response = opener.open(url)
    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        raise Exception(
            "Got incorrect response code while requesting channel list. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        raise Exception("Did not receive json, something wrong: " + response_text)

    if json_object["status"] != "ok":
        raise Exception("Invalid response: " + response_text)

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

    streamurl = None

    url = API_ENDPOINT + "/api/v1.4/get/content/live-streams/" + data_url + "?include=quality"
    opener = get_url_opener()
    opener.addheaders.append(('Authorization', "Bearer " + config.get_setting("token")))
    response = opener.open(url)

    response_text = response.read()
    response_code = response.getcode()

    if response_code != 200:
        config.set_setting("logged_in", "false")
        raise Exception(
            "Got incorrect response code while requesting stream info. Reponse code: " + response_code + ";\nText: " + response_text)

    json_object = None
    try:
        json_object = json.loads(response_text)
    except ValueError, e:
        config.set_setting("logged_in", "false")
        raise Exception("Did not receive json, something wrong: " + response_text)

    stream_links = {}

    for stream in json_object["data"]:

        if stream["type"] != "live-streams":
            continue

        url = stream["attributes"]["stream-url"] + "&auth_token=app_" + config.get_setting("token")

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
