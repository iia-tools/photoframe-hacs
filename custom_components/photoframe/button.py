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
        key="brightness_settings",
        translation_key="brightness_settings",
        icon="mdi:brightness-6",
        action="brightness_settings",
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
