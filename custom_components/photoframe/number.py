"""Number entities for Smart Frame."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import PERCENTAGE

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator
from .entity import SmartFrameEntity


@dataclass(frozen=True, kw_only=True)
class SmartFrameNumberEntityDescription(NumberEntityDescription):
    """Describe a Smart Frame number."""

    status_key: str
    action: str
    value_param: str


NUMBERS: tuple[SmartFrameNumberEntityDescription, ...] = (
    SmartFrameNumberEntityDescription(
        key="music_volume",
        translation_key="music_volume",
        icon="mdi:music-note",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        status_key="music_volume",
        action="set_music_volume",
        value_param="volume",
    ),
    SmartFrameNumberEntityDescription(
        key="system_volume",
        translation_key="system_volume",
        icon="mdi:volume-high",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        status_key="system_volume",
        action="set_system_volume",
        value_param="volume",
    ),
    SmartFrameNumberEntityDescription(
        key="screen_brightness",
        translation_key="screen_brightness",
        icon="mdi:brightness-6",
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        status_key="screen_brightness",
        action="set_screen_brightness",
        value_param="brightness",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Smart Frame numbers."""
    coordinator: SmartFrameCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(SmartFrameNumber(coordinator, description) for description in NUMBERS)


class SmartFrameNumber(SmartFrameEntity, NumberEntity):
    """Smart Frame number entity."""

    entity_description: SmartFrameNumberEntityDescription

    def __init__(
        self,
        coordinator: SmartFrameCoordinator,
        description: SmartFrameNumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the current number value."""
        value = (self.coordinator.data or {}).get(self.entity_description.status_key)
        if isinstance(value, int | float):
            return float(value)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        await self.async_send_action(
            self.entity_description.action,
            **{self.entity_description.value_param: int(value)},
        )
