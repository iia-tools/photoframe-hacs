"""Button entities for Smart Frame."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator
from .entity import SmartFrameEntity


@dataclass(frozen=True, kw_only=True)
class SmartFrameButtonEntityDescription(ButtonEntityDescription):
    """Describe a Smart Frame button."""

    action: str
    params: dict[str, Any] = field(default_factory=dict)


BUTTONS: tuple[SmartFrameButtonEntityDescription, ...] = (
    SmartFrameButtonEntityDescription(
        key="start",
        translation_key="start",
        icon="mdi:play",
        action="start",
    ),
    SmartFrameButtonEntityDescription(
        key="previous",
        translation_key="previous",
        icon="mdi:skip-previous",
        action="previous",
    ),
    SmartFrameButtonEntityDescription(
        key="next",
        translation_key="next",
        icon="mdi:skip-next",
        action="next",
    ),
    SmartFrameButtonEntityDescription(
        key="sync",
        translation_key="sync",
        icon="mdi:sync",
        action="sync",
    ),
    SmartFrameButtonEntityDescription(
        key="refresh_weather",
        translation_key="refresh_weather",
        icon="mdi:weather-partly-cloudy",
        action="refresh_weather",
    ),
    SmartFrameButtonEntityDescription(
        key="refresh_location",
        translation_key="refresh_location",
        icon="mdi:crosshairs-gps",
        action="refresh_location",
    ),
    SmartFrameButtonEntityDescription(
        key="screen_off_15m",
        translation_key="screen_off_15m",
        icon="mdi:monitor-off",
        action="screen_off",
        params={"minutes": 15},
    ),
    SmartFrameButtonEntityDescription(
        key="screen_off_until_on",
        translation_key="screen_off_until_on",
        icon="mdi:monitor-off",
        action="screen_off",
        params={"seconds": 0},
    ),
    SmartFrameButtonEntityDescription(
        key="screen_on",
        translation_key="screen_on",
        icon="mdi:monitor",
        action="screen_on",
    ),
    SmartFrameButtonEntityDescription(
        key="wifi_settings",
        translation_key="wifi_settings",
        icon="mdi:wifi-cog",
        action="wifi_settings",
    ),
    SmartFrameButtonEntityDescription(
        key="wifi_on",
        translation_key="wifi_on",
        icon="mdi:wifi",
        action="wifi_on",
    ),
    SmartFrameButtonEntityDescription(
        key="wifi_off",
        translation_key="wifi_off",
        icon="mdi:wifi-off",
        action="wifi_off",
    ),
    SmartFrameButtonEntityDescription(
        key="bluetooth_settings",
        translation_key="bluetooth_settings",
        icon="mdi:bluetooth-settings",
        action="bluetooth_settings",
    ),
    SmartFrameButtonEntityDescription(
        key="bluetooth_on",
        translation_key="bluetooth_on",
        icon="mdi:bluetooth",
        action="bluetooth_on",
    ),
    SmartFrameButtonEntityDescription(
        key="bluetooth_off",
        translation_key="bluetooth_off",
        icon="mdi:bluetooth-off",
        action="bluetooth_off",
    ),
    SmartFrameButtonEntityDescription(
        key="brightness_settings",
        translation_key="brightness_settings",
        icon="mdi:brightness-6",
        action="brightness_settings",
    ),
    SmartFrameButtonEntityDescription(
        key="auto_rotate_on",
        translation_key="auto_rotate_on",
        icon="mdi:phone-rotate-landscape",
        action="auto_rotate_on",
    ),
    SmartFrameButtonEntityDescription(
        key="auto_rotate_off",
        translation_key="auto_rotate_off",
        icon="mdi:screen-rotation-lock",
        action="auto_rotate_off",
    ),
    SmartFrameButtonEntityDescription(
        key="rotate_0",
        translation_key="rotate_0",
        icon="mdi:rotate-360",
        action="rotate_0",
    ),
    SmartFrameButtonEntityDescription(
        key="rotate_90",
        translation_key="rotate_90",
        icon="mdi:rotate-right",
        action="rotate_90",
    ),
    SmartFrameButtonEntityDescription(
        key="rotate_180",
        translation_key="rotate_180",
        icon="mdi:rotate-3d-variant",
        action="rotate_180",
    ),
    SmartFrameButtonEntityDescription(
        key="rotate_270",
        translation_key="rotate_270",
        icon="mdi:rotate-left",
        action="rotate_270",
    ),
    SmartFrameButtonEntityDescription(
        key="accessibility_settings",
        translation_key="accessibility_settings",
        icon="mdi:gesture-tap",
        action="accessibility_settings",
    ),
    SmartFrameButtonEntityDescription(
        key="return_app",
        translation_key="return_app",
        icon="mdi:application-import",
        action="return_app",
    ),
    SmartFrameButtonEntityDescription(
        key="mute",
        translation_key="mute",
        icon="mdi:volume-off",
        action="mute",
    ),
    SmartFrameButtonEntityDescription(
        key="unmute",
        translation_key="unmute",
        icon="mdi:volume-high",
        action="unmute",
    ),
    SmartFrameButtonEntityDescription(
        key="global_back",
        translation_key="global_back",
        icon="mdi:keyboard-backspace",
        action="global_back",
    ),
    SmartFrameButtonEntityDescription(
        key="global_home",
        translation_key="global_home",
        icon="mdi:home",
        action="global_home",
    ),
    SmartFrameButtonEntityDescription(
        key="clear_cache",
        translation_key="clear_cache",
        icon="mdi:delete-sweep",
        action="clear_cache",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Smart Frame buttons."""
    coordinator: SmartFrameCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SmartFrameButton(coordinator, description) for description in BUTTONS)


class SmartFrameButton(SmartFrameEntity, ButtonEntity):
    """Smart Frame button entity."""

    entity_description: SmartFrameButtonEntityDescription

    def __init__(
        self,
        coordinator: SmartFrameCoordinator,
        description: SmartFrameButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Handle button press."""
        await self.async_send_action(
            self.entity_description.action,
            **self.entity_description.params,
        )
