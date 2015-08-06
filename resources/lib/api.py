import cookielib, urllib, urllib2
import sys
import utils
import re
import base64
from BeautifulSoup import BeautifulSoup

import config

try:
    import xbmc, xbmcplugin
except:
    pass


def get_url_opener(referrer=None):
    cookiejar = config.get_cookiejar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    opener.addheaders = [

        #('Referer', 'https://m.lattelecom.tv/authorization/'),
        ('Origin', 'https://m.lattelecom.tv'),
        # ('Accept-Encoding','gzip,deflate,sdch'),
        ('Accept-Language', 'en-US,en;q=0.8,lv;q=0.6'),
        ('User-Agent',
         'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('Cache-Control', 'max-age=0'),
        ('Connection', 'keep-alive'),
        ('DNT', '1'),
    ]
    if (referrer is not None):
        opener.addheaders.append(('Referer', referrer))

    return opener, cookiejar


def login():
    logged_in = config.get_config("logged_in")
    if (logged_in is not None and len(logged_in) > 0):
        return

    config.delete_cookiejar()

    opener, cookiejar = get_url_opener()
    response = opener.open('https://m.lattelecom.tv/authorization')
    response_code = response.getcode()
    if response_code != 200:
        raise Exception("Cannot get session id")
    response_text = response.read()

    if "captcha" in response_text:
        raise Exception("captcha not implemented")

    phpsessid = None
    for cookie in cookiejar:
        if cookie.name == 'PHPSESSID':
            phpsessid = cookie.value
    if phpsessid is None:
        raise Exception("phpsessid not found")

    bitrate_cookie = cookielib.Cookie(version=0, name='MobBitr', value='1', port=None, port_specified=False,
                                      domain='m.lattelecom.tv', domain_specified=False, domain_initial_dot=False, path='/',
                                      path_specified=True, secure=False, expires=None, discard=True, comment=None,
                                      comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    cookiejar.set_cookie(bitrate_cookie)
    cookiejar.save(filename=config.get_cookiejar_file(), ignore_discard=True)

    # some extra requests for auth (big brother)
    match = re.search('src="(/auth/[\d]+\.gif)"', response_text)
    if match is None:
        config.delete_cookiejar()
        # @TODO maybe retry?
        raise Exception("auth gif not found")

    gif_path = 'https://m.lattelecom.tv' + match.group(1)
    opener, cookiejar = get_url_opener('https://m.lattelecom.tv/authorization')
    opener.open(gif_path)

    gif64 = base64.b64encode(gif_path)
    opener, cookiejar = get_url_opener('https://m.lattelecom.tv/authorization')
    url = 'https://auth.lattelecom.lv/url/session?sid=' + phpsessid + '&sp=OPT&retUrl=' + gif64 + '='
    opener.open(url)

    # perform real login
    opener, cookiejar = get_url_opener()
    username = config.get_config("username")
    password = config.get_config('password')
    params = urllib.urlencode(dict(login='yes', email=username, passw=password))
    utils.log(params)

    response = opener.open('https://m.lattelecom.tv/authorization/', params)
    response_text = response.read()
    if re.search('is_logged_in=true', response_text) is None:
        print response_text
        raise Exception("login failed")

    cookiejar.save(filename=config.get_cookiejar_file(), ignore_discard=True)
    config.set_config("logged_in", "yeah!")

    utils.log("login success!")

def get_channels():
    login()

    url = 'https://m.lattelecom.tv/tiesraide'
    opener, cookiejar = get_url_opener()
    response = opener.open(url)
    response_text = response.read()
    soup = BeautifulSoup(response_text)

    channels = []
    for el in soup.findAll("div", "chanel_list_info"):
        channel_el =  el.find('span', "channel")
        if channel_el is None:
            continue

        if not el.has_key("data-url"):
            continue

        channel = channel_el.text

        channel_info_el =  el.find('span', "rinfo")
        if channel_info_el is None:
            channel_info = ""
        else:
            channel_info = channel_info_el.text

        data_url = el['data-url']

        channels.append({
            'channel': channel,
            'channel-info': channel_info,
            'data-url': data_url
        })

    return channels

def get_stream_url(data_url):

    url = 'https://m.lattelecom.tv'+data_url
    opener, cookiejar = get_url_opener()
    response = opener.open(url)
    response_text = response.read()
    soup = BeautifulSoup(response_text)
    streamurltag = soup.find(type="application/x-mpegURL")
    streamurl = streamurltag.get('src')
    return streamurl

    # bitrate = "1"
    # url = 'https://m.lattelecom.tv/free_origin?show_origin=1&type=1&chan=' + chan_url +'&streamurl=' + streamurl + '&bitrate=' + bitrate
    # opener, cookiejar = get_url_opener()
    # response = opener.open(url)
    # response_text = response.read()
    # return response_text

    #pass
    #https://m.lattelecom.tv/free_origin?show_origin=1&type=1&chan=ltv1&streamurl=ltv1_lv&bitrate=1
