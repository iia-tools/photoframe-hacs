"""Sensor entities for Smart Frame."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfInformation, UnitOfTime
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator
from .entity import SmartFrameEntity


def _value(data: dict[str, Any], key: str) -> StateType:
    """Return a Home Assistant state value."""
    value = data.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float | str):
        return value
    return None


def _cache_mb(data: dict[str, Any]) -> StateType:
    """Return cache size in MB."""
    cache_bytes = data.get("cache_bytes")
    if isinstance(cache_bytes, int | float):
        return round(cache_bytes / 1024 / 1024, 1)
    return None


def _current_file(data: dict[str, Any]) -> StateType:
    """Return the current media file name."""
    current = data.get("current")
    if isinstance(current, dict):
        file_name = current.get("file_name")
        if isinstance(file_name, str):
            return file_name
    return None


def _state_attributes(data: dict[str, Any]) -> Mapping[str, Any]:
    """Return status attributes."""
    keys = (
        "state_text",
        "screen_blackout",
        "temporary_screen_off",
        "screen_off_until_on",
        "screen_brightness",
        "screen_auto_brightness",
        "screen_brightness_min",
        "screen_brightness_max",
        "screen_brightness_system_writable",
        "screen_auto_rotate",
        "screen_rotation",
        "screen_rotation_degrees",
        "wifi_state",
        "bluetooth_state",
        "system_muted",
        "accessibility_control",
        "playback_folder",
        "recent_input_events",
        "storage_summary",
        "remote_port",
    )
    return {key: data[key] for key in keys if key in data}


def _current_attributes(data: dict[str, Any]) -> Mapping[str, Any] | None:
    """Return current media attributes."""
    current = data.get("current")
    if not isinstance(current, dict):
        return None
    return {key: value for key, value in current.items() if key != "file_name"}


@dataclass(frozen=True, kw_only=True)
class SmartFrameSensorEntityDescription(SensorEntityDescription):
    """Describe a Smart Frame sensor."""

    value_fn: Callable[[dict[str, Any]], StateType]
    attributes_fn: Callable[[dict[str, Any]], Mapping[str, Any] | None] | None = None


SENSORS: tuple[SmartFrameSensorEntityDescription, ...] = (
    SmartFrameSensorEntityDescription(
        key="state",
        translation_key="state",
        icon="mdi:image-frame",
        value_fn=lambda data: _value(data, "state"),
        attributes_fn=_state_attributes,
    ),
    SmartFrameSensorEntityDescription(
        key="photo_count",
        translation_key="photo_count",
        icon="mdi:image-multiple",
        value_fn=lambda data: _value(data, "photo_count"),
    ),
    SmartFrameSensorEntityDescription(
        key="video_count",
        translation_key="video_count",
        icon="mdi:video",
        value_fn=lambda data: _value(data, "video_count"),
    ),
    SmartFrameSensorEntityDescription(
        key="music_count",
        translation_key="music_count",
        icon="mdi:music",
        value_fn=lambda data: _value(data, "music_count"),
    ),
    SmartFrameSensorEntityDescription(
        key="cache_size",
        translation_key="cache_size",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_cache_mb,
    ),
    SmartFrameSensorEntityDescription(
        key="screen_off_remaining",
        translation_key="screen_off_remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
        value_fn=lambda data: _value(data, "screen_off_remaining_seconds"),
    ),
    SmartFrameSensorEntityDescription(
        key="current_media",
        translation_key="current_media",
        icon="mdi:file-image-outline",
        value_fn=_current_file,
        attributes_fn=_current_attributes,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Smart Frame sensors."""
    coordinator: SmartFrameCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SmartFrameSensor(coordinator, description) for description in SENSORS)


class SmartFrameSensor(SmartFrameEntity, SensorEntity):
    """Smart Frame sensor entity."""

    entity_description: SmartFrameSensorEntityDescription

    def __init__(
        self,
        coordinator: SmartFrameCoordinator,
        description: SmartFrameSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator.data or {})
