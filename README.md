# Lattelecom.tv / Shortcut.lv live TV XBMC/Kodi addon [![Build Status](https://travis-ci.org/Janhouse/xbmc-lattelecom.tv.svg?branch=master)](https://travis-ci.org/Janhouse/xbmc-lattelecom.tv)

This is a community maintained unofficial Lattelecom.tv/Shortcut.lv XBMC/Kodi addon.
**To use it, you must have an account on Lattelecom.tv**.

_Currently this plugin uses Shortcut.lv mobile application API._

## Usage

If you want to receive **automatic updates**, install repository addon from the following link. Then install Lattelecom.tv addon from the repository.
https://janhouse.github.io/kodi-repo-lattelecomtv/datadir/repository.lattelecomtv/repository.lattelecomtv-1.0.0.zip

Alternatively download this repository as a .zip file or download one of the releases from Github's releases section.
Then install it as .zip file in Kodi addons section.

__Make sure you go to addon settings to input your credentials.__

![Alt text](/screenshots/list.png?raw=true "Channel list in Kodi")

![Alt text](/screenshots/nick.png?raw=true "Streaming TV channel")

## Development
Running tests:
`python -m unittest test.test_get_url_opener`

Accepted environment variables:

`TEST_INTERNATIONAL` set this value to skip tests that work only from Lattelecom network. (Useful when running automated tests from Travis)

`TEST_PASSWORD` Shortcut.lv password 

`TEST_USER` Shortcut.lv username