"""Camera entity for Smart Frame."""

from __future__ import annotations

from homeassistant.components.camera import Camera
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import SmartFrameCoordinator


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Smart Frame camera entities."""
    coordinator: SmartFrameCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartFrameCurrentPhotoCamera(coordinator)])


class SmartFrameCurrentPhotoCamera(Camera):
    """Camera entity exposing the currently displayed frame photo."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_photo"

    def __init__(self, coordinator: SmartFrameCoordinator) -> None:
        """Initialize the current photo camera."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry_unique_id}_current_photo"
        self.content_type = "image/jpeg"

    @property
    def available(self) -> bool:
        """Return if the Smart Frame is reachable."""
        return self.coordinator.last_update_success

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

    async def async_camera_image(
        self,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes | None:
        """Return the currently displayed photo."""
        return await self.coordinator.client.async_get_current_image()
