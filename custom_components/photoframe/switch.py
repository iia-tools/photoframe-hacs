"""Switch entities for Smart Frame."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator
from .entity import SmartFrameEntity


@dataclass(frozen=True, kw_only=True)
class SmartFrameSwitchEntityDescription(SwitchEntityDescription):
    """Describe a Smart Frame switch."""

    status_key: str
    action: str | None = None
    turn_on_action: str | None = None
    turn_off_action: str | None = None
    value_fn: Callable[[dict[str, Any], str], bool | None] | None = None


def _bool_value(data: dict[str, Any], status_key: str) -> bool | None:
    """Return a boolean state value."""
    value = data.get(status_key)
    if isinstance(value, bool):
        return value
    return None


def _enabled_state(data: dict[str, Any], status_key: str) -> bool | None:
    """Return whether a localized device state means enabled."""
    value = data.get(status_key)
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    return (
        "켜짐" in value
        or "enabled" in normalized
        or normalized == "on"
        or " on" in normalized
        or "true" in normalized
    )


SWITCHES: tuple[SmartFrameSwitchEntityDescription, ...] = (
    SmartFrameSwitchEntityDescription(
        key="video_playback",
        translation_key="video_playback",
        icon="mdi:video-switch",
        status_key="video_playback",
        action="set_video_playback",
    ),
    SmartFrameSwitchEntityDescription(
        key="motion_photo_playback",
        translation_key="motion_photo_playback",
        icon="mdi:motion-play-outline",
        status_key="motion_photo_playback",
        action="set_motion_photo_playback",
    ),
    SmartFrameSwitchEntityDescription(
        key="background_music",
        translation_key="background_music",
        icon="mdi:music",
        status_key="background_music",
        action="set_background_music",
    ),
    SmartFrameSwitchEntityDescription(
        key="shuffle",
        translation_key="shuffle",
        icon="mdi:shuffle-variant",
        status_key="shuffle",
        action="set_shuffle",
    ),
    SmartFrameSwitchEntityDescription(
        key="screen_auto_brightness",
        translation_key="screen_auto_brightness",
        icon="mdi:brightness-auto",
        status_key="screen_auto_brightness",
        action="set_screen_auto_brightness",
    ),
    SmartFrameSwitchEntityDescription(
        key="screen_auto_rotate",
        translation_key="screen_auto_rotate",
        icon="mdi:screen-rotation",
        status_key="screen_auto_rotate",
        turn_on_action="auto_rotate_on",
        turn_off_action="auto_rotate_off",
    ),
    SmartFrameSwitchEntityDescription(
        key="wifi",
        translation_key="wifi",
        icon="mdi:wifi",
        status_key="wifi_state",
        turn_on_action="wifi_on",
        turn_off_action="wifi_off",
        value_fn=_enabled_state,
    ),
    SmartFrameSwitchEntityDescription(
        key="bluetooth",
        translation_key="bluetooth",
        icon="mdi:bluetooth",
        status_key="bluetooth_state",
        turn_on_action="bluetooth_on",
        turn_off_action="bluetooth_off",
        value_fn=_enabled_state,
    ),
    SmartFrameSwitchEntityDescription(
        key="system_mute",
        translation_key="system_mute",
        icon="mdi:volume-off",
        status_key="system_muted",
        turn_on_action="mute",
        turn_off_action="unmute",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Smart Frame switches."""
    coordinator: SmartFrameCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SmartFrameSwitch(coordinator, description) for description in SWITCHES)


class SmartFrameSwitch(SmartFrameEntity, SwitchEntity):
    """Smart Frame switch entity."""

    entity_description: SmartFrameSwitchEntityDescription

    def __init__(
        self,
        coordinator: SmartFrameCoordinator,
        description: SmartFrameSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return whether the switch is on."""
        data = self.coordinator.data or {}
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(data, self.entity_description.status_key)
        return _bool_value(data, self.entity_description.status_key)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        if self.entity_description.turn_on_action is not None:
            await self.async_send_action(self.entity_description.turn_on_action)
            return
        if self.entity_description.action is not None:
            await self.async_send_action(self.entity_description.action, enabled=True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        if self.entity_description.turn_off_action is not None:
            await self.async_send_action(self.entity_description.turn_off_action)
            return
        if self.entity_description.action is not None:
            await self.async_send_action(self.entity_description.action, enabled=False)
