from unittest import TestCase
from resources.lib import api
import os

def get_cookiejar_file():
    return "/tmp/xbmc-lattelecomlv-cookiejar"

def get_config(key):
    if key == 'username':
        return ''
    elif key == 'password':
        return ''
def set_config(key, value):
    pass

def reset_cookies():
    try:
        os.remove(get_cookiejar_file())
    except:
        pass

def patch_config():
    from resources.lib.api import config
    config.get_config = get_config
    config.get_cookiejar_file = get_cookiejar_file
    config.set_config = set_config

class TestGet_url_opener(TestCase):
    def test_login_success(self):
        reset_cookies()
        patch_config()

        try:
            api.login()
        except Exception as e:
            self.fail(e.message)

    def test_get_channels(self):
        reset_cookies()
        patch_config()

        try:
            channels = api.get_channels()
            self.assertGreater(len(channels), 0)
        except Exception as e:
            self.fail(e.message)

    def test_get_stream_url(self):
        reset_cookies()
        patch_config()

        try:
            api.login()
            stream_url = api.get_stream_url("/tiesraide/satori_360tv")
            self.assertIsNotNone(stream_url)
        except Exception as e:
            self.fail(e.message)
