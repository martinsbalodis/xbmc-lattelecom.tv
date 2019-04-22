# Lattelecom.tv / Shortcut.lv live TV XBMC/Kodi addon

This is an XBMC/Kodi plugin for lattelecom.tv / shortcut.lv live TV stream.
To use this you must have an account on lattelecom.tv.

Currently this plugin uses Shortcut.lv mobile application API.

## Usage
Install .zip file from Github repository Releases section in XBMC/Kodi.

Or download this repository as zip and extract it into the xbmc/kodi addons 
directory.

On Linux it is located in ~/.xbmc/addons . After copying the plugin to addons 
directory restart the player and it should be available.

__Make sure you go to addon settings to input your credentials.__

## Requirements for TV section and EPG

Addon has listed necessary addons but since not all of them are available in Kodi repository for all platforms, 
some of them are  marked as optional, more specifically `IPTV Simple` and `Inputstream Adaptive`.

`IPTV Simple` addon is necessary to enable TV section and EPG. After installing this addon, go to `Lattelecom Live TV` 
addon settings and click `Configure PVR IPTVSimple addon automatically` and then `Rebuild EPG data`. After that 
restart Kodi and it should work.

`Inputstream Adaptive` will make switching between channels almost instant. If stream does not work for some reason, 
try disabling this addon.

## Screenshots

Legacy channel list when not using TV view

![Alt text](/screenshots/list.png?raw=true "Channel list in Kodi")

Timeline in TV section

![Alt text](/screenshots/timeline.png?raw=true "TV timeline in Kodi")

Channel view in TV section

![Alt text](/screenshots/channels.png?raw=true "Channels in TV section of Kodi")

TV stream with EPG information

![Alt text](/screenshots/stream.png?raw=true "Stream view in Kodi")

Channel overlay with EPG information

![Alt text](/screenshots/overlay.png?raw=true "Channel overlay in Kodi")

Channel guide overlay

![Alt text](/screenshots/guide.png?raw=true "Channel guide overlay in Kodi")

Addon settings section

![Alt text](/screenshots/settings.png?raw=true "Addon settings in Kodi")

## Development
Running tests:
`python -m unittest test.test_get_url_opener`

Accepted environment variables:

`TEST_INTERNATIONAL` set this value to skip tests that work only from Lattelecom network. (Useful when running automated tests from Travis)

`TEST_PASSWORD` Shortcut.lv password 

`TEST_USER` Shortcut.lv username