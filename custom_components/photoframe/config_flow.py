"""Config flow for Smart Frame."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, urlunparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    SmartFrameApiClient,
    SmartFrameAuthError,
    SmartFrameCannotConnect,
    SmartFrameError,
)
from .const import CONF_PIN, DOMAIN


def _normalize_url(value: str) -> str:
    """Normalize a user supplied Smart Frame URL."""
    value = value.strip()
    if "://" not in value:
        value = f"http://{value}"

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("invalid URL")

    path = parsed.path.rstrip("/")
    for suffix in ("/api/status", "/api/action"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break

    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", "")).rstrip("/")


def _unique_id_from_url(base_url: str) -> str:
    """Build a config-entry unique ID from the normalized URL."""
    parsed = urlparse(base_url)
    return parsed.netloc.lower()


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the Smart Frame connection details."""
    session = async_get_clientsession(hass)
    client = SmartFrameApiClient(session, data[CONF_URL], data[CONF_PIN])
    status = await client.async_get_status()
    title = str(status.get("name") or "Smart Frame")
    return {"title": title, "unique_id": _unique_id_from_url(data[CONF_URL])}


class SmartFrameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Frame."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        super().__init__()
        self._reauth_entry: ConfigEntry | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data = dict(user_input)
            try:
                data[CONF_URL] = _normalize_url(data[CONF_URL])
                data[CONF_PIN] = str(data[CONF_PIN]).strip()
                info = await _validate_input(self.hass, data)
            except ValueError:
                errors["base"] = "invalid_url"
            except SmartFrameAuthError:
                errors["base"] = "invalid_auth"
            except SmartFrameCannotConnect:
                errors["base"] = "cannot_connect"
            except SmartFrameError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured(updates=data)
                return self.async_create_entry(title=info["title"], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Required(CONF_PIN): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        """Handle reauthentication."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        """Ask the user for a new PIN."""
        errors: dict[str, str] = {}

        if self._reauth_entry is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            data = dict(self._reauth_entry.data)
            data[CONF_PIN] = str(user_input[CONF_PIN]).strip()
            try:
                await _validate_input(self.hass, data)
            except SmartFrameAuthError:
                errors["base"] = "invalid_auth"
            except SmartFrameCannotConnect:
                errors["base"] = "cannot_connect"
            except SmartFrameError:
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(self._reauth_entry, data=data)
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PIN): str}),
            errors=errors,
        )
