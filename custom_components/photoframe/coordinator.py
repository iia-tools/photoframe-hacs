"""Data coordinator for Smart Frame."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SmartFrameApiClient,
    SmartFrameAuthError,
    SmartFrameCannotConnect,
    SmartFrameError,
    SmartFrameRateLimited,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartFrameCoordinator(DataUpdateCoordinator):
    """Fetch Smart Frame status for all entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: SmartFrameApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=DEFAULT_SCAN_INTERVAL,
            always_update=False,
        )
        self.client = client
        self.config_entry = config_entry
        self.entry_unique_id = config_entry.unique_id or config_entry.entry_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch current status from the Smart Frame."""
        try:
            return await self.client.async_get_status()
        except SmartFrameAuthError as err:
            raise ConfigEntryAuthFailed from err
        except SmartFrameRateLimited as err:
            raise UpdateFailed("Smart Frame is rate limiting PIN attempts") from err
        except SmartFrameCannotConnect as err:
            raise UpdateFailed(f"Cannot connect to Smart Frame: {err}") from err
        except SmartFrameError as err:
            raise UpdateFailed(f"Smart Frame API error: {err}") from err
