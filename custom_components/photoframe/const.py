"""Constants for the Smart Frame integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "photoframe"

CONF_PIN = "pin"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=15)

PLATFORMS = [
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]
