from unittest import TestCase
from resources.lib import api
import os

def get_config(key):
    if key == 'username':
        return ''
    elif key == 'password':
        return ''
def set_config(key, value):
    pass

def patch_config():
    from resources.lib.api import config
    config.get_config = get_config
    config.set_config = set_config

class TestGet_url_opener(TestCase):
    def test_login_success(self):
        patch_config()
        try:
            api.login()
        except Exception as e:
            self.fail(e.message)

    def test_get_channels(self):
        patch_config()

        try:
            channels = api.get_channels()
            self.assertGreater(len(channels), 0)
        except Exception as e:
            self.fail(e.message)

    def test_get_stream_url(self):
        patch_config()

        try:
            api.login()
            # 101 - LTV 1
            stream_url = api.get_stream_url("101")
            self.assertIsNotNone(stream_url)
        except Exception as e:
            self.fail(e.message)
