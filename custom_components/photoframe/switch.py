"""Switch entities for Smart Frame."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator
from .entity import SmartFrameEntity


@dataclass(frozen=True, kw_only=True)
class SmartFrameSwitchEntityDescription(SwitchEntityDescription):
    """Describe a Smart Frame switch."""

    status_key: str
    action: str


SWITCHES: tuple[SmartFrameSwitchEntityDescription, ...] = (
    SmartFrameSwitchEntityDescription(
        key="video_playback",
        translation_key="video_playback",
        icon="mdi:video-switch",
        status_key="video_playback",
        action="set_video_playback",
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
        value = (self.coordinator.data or {}).get(self.entity_description.status_key)
        if isinstance(value, bool):
            return value
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.async_send_action(self.entity_description.action, enabled=True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.async_send_action(self.entity_description.action, enabled=False)
