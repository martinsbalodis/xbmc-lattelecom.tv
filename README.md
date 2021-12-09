# Tet+ / Lattelecom.tv / Shortcut.lv live TV XBMC/Kodi addon [![Build Status](https://travis-ci.org/Janhouse/xbmc-lattelecom.tv.svg?branch=master)](https://travis-ci.org/Janhouse/xbmc-lattelecom.tv)

This is a community maintained unofficial Lattelecom.tv/Shortcut.lv XBMC/Kodi addon.
**To use it, you must have an account on Lattelecom.tv**.

_Currently this plugin uses Shortcut.lv mobile application API._

## Usage

If you want to receive **automatic updates**, install repository addon from the following link. Then install Lattelecom.tv addon from the repository.
https://janhouse.github.io/kodi-repo-lattelecomtv/datadir/repository.lattelecomtv/repository.lattelecomtv-1.0.0.zip

Alternatively download this repository as a .zip file or download one of the releases from Github's releases section.
Then install it as .zip file in Kodi addons section.

__Make sure you go to addon settings to input your credentials.__

## Requirements for TV section and EPG

Addon has listed necessary addons but since not all of them are available in Kodi repository for all platforms, 
some of them are  marked as optional, more specifically `IPTV Simple` and `Inputstream Adaptive`.

`IPTV Simple` addon is necessary to enable TV section and EPG. After installing this addon, go to `Lattelecom Live TV` 
addon settings and click `Configure PVR IPTVSimple addon automatically` and then `Rebuild EPG data`. After that 
restart Kodi and it should work.

`Inputstream Adaptive` will make switching between channels almost instant. If stream does not work for some reason, 
try disabling this addon.

### Fixing incorrect EPG time offset

In some cases time zone settings are ignored by Kodi and EPG data is shifted incorrectly. To fix this go to IPTVSimple 
addon settings, set the correct time shift and then clear EPG databse by going to Kodi `Settings > PVR & Live TV > Guide > Clear data`

## Screenshots

Legacy channel list when not using TV view

![Alt text](screenshots/list.png?raw=true "Channel list in Kodi")

Timeline in TV section

![Alt text](screenshots/timeline.png?raw=true "TV timeline in Kodi")

Channel view in TV section

![Alt text](screenshots/channels.png?raw=true "Channels in TV section of Kodi")

TV stream with EPG information

![Alt text](screenshots/stream.png?raw=true "Stream view in Kodi")

Channel overlay with EPG information

![Alt text](screenshots/overlay.png?raw=true "Channel overlay in Kodi")

Channel guide overlay

![Alt text](screenshots/guide.png?raw=true "Channel guide overlay in Kodi")

Addon settings section

![Alt text](screenshots/settings.png?raw=true "Addon settings in Kodi")

## Development

### Setup

Use Python 2

`virtualenv -p /usr/bin/python2.7 venv/`

Activate the environment

`source venv/bin/activate`

Install dependencies

```
pip install mock
pip install pytz
pip install Kodistubs
```

### Running tests:
`python -m unittest discover`

Accepted environment variables:

`TEST_INTERNATIONAL` set this value to skip tests that work only from Lattelecom network. (Useful when running automated tests from Travis)

`TEST_PASSWORD` Shortcut.lv password 

`TEST_USER` Shortcut.lv username
