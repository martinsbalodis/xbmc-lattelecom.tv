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

![Alt text](/screenshots/list.png?raw=true "Channel list in Kodi")

![Alt text](/screenshots/nick.png?raw=true "Streaming TV channel")

## Development
Running tests:
`python -m unittest test.test_get_url_opener`

## TODO:
* Implement EPG
