import os
import unittest
from unittest import TestCase

from lib import api

skip_regional = False
if "TEST_INTERNATIONAL" in os.environ:
    skip_regional = True

def patch_config():
    # Fill your username and password to run tests or pass them in environment variables TEST_USER and TEST_PASSWORD
    settings = {
        'token': '',
        'username': '',
        'password': '',
        'logged_in': False,
        'configured': True,
        'uid': None,
        'last_login': "1970-01-01 23:59:00.000000",
    }

    if "TEST_USER" in os.environ:
        settings['username'] = os.environ['TEST_USER']
    if "TEST_PASSWORD" in os.environ:
        settings['password'] = os.environ['TEST_PASSWORD']

    def get_config(key):
        return settings[key]

    def set_config(key, value):
        settings[key] = value

    from lib.api import config
    config.get_config = get_config
    config.set_config = set_config
    config.get_setting = get_config
    config.set_setting = set_config


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

    @unittest.skipIf(skip_regional, "Supported only from Latvian IP addresses")
    def test_get_stream_url(self):
        patch_config()

        try:
            api.login()
            # 101 - LTV 1
            stream_url = api.get_stream_url("101")
            self.assertIsNotNone(stream_url)
        except Exception as e:
            self.fail(e.message)
