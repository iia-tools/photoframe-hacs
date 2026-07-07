# Smart Frame for Home Assistant

Home Assistant custom integration for the PhotoFrame Android smart frame app.

This repository is intended for HACS installation. It contains only the Home
Assistant integration files and does not include the Android app source.

## Installation with HACS

1. In the PhotoFrame app, open settings.
2. In `Remote / Security`, enable remote management on the local network.
3. Note the displayed URL and PIN, for example `http://192.168.50.182:8088`.
4. In Home Assistant, open HACS.
5. Add this repository as a custom repository:
   - Repository: `https://github.com/iia-tools/photoframe-hacs`
   - Category: `Integration`
6. Install `Smart Frame`.
7. Restart Home Assistant.
8. Go to `Settings` > `Devices & services` > `Add integration`.
9. Search for `Smart Frame` and enter the frame URL and PIN.

## Entities

The integration creates one Smart Frame device with these entities:

| Type | Entities |
| --- | --- |
| Sensor | Status, photo count, video count, music count, cache size, screen off remaining, current media |
| Button | Start slideshow, previous, next, sync now, screen off for 15 minutes, screen on, clear cache |
| Number | Music volume, system volume |
| Switch | Video playback |

## Notes

- Keep Home Assistant and the smart frame on the same trusted LAN.
- Do not expose the frame's remote management port to the internet.
- If the frame IP changes, reserve a DHCP address for it in your router.
