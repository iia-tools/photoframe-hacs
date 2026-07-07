"""Base entity helpers for Smart Frame."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import SmartFrameError
from .const import DOMAIN
from .coordinator import SmartFrameCoordinator


class SmartFrameEntity(CoordinatorEntity):
    """Base Smart Frame entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SmartFrameCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_unique_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the Smart Frame."""
        data = self.coordinator.data or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry_unique_id)},
            manufacturer="Codex",
            model="Android Smart Frame",
            name=data.get("name") or self.coordinator.config_entry.title,
        )

    async def async_send_action(self, action: str, **params: Any) -> None:
        """Send an action and refresh state."""
        try:
            await self.coordinator.client.async_action(action, **params)
        except SmartFrameError as err:
            raise HomeAssistantError(f"Smart Frame action failed: {err}") from err
        await self.coordinator.async_request_refresh()
