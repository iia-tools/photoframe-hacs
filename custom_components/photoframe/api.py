"""Local HTTP client for Smart Frame."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout, ContentTypeError


class SmartFrameError(Exception):
    """Base error for Smart Frame API failures."""


class SmartFrameCannotConnect(SmartFrameError):
    """Raised when the Smart Frame cannot be reached."""


class SmartFrameAuthError(SmartFrameError):
    """Raised when the Smart Frame PIN is rejected."""


class SmartFrameRateLimited(SmartFrameError):
    """Raised when the Smart Frame temporarily rate limits PIN attempts."""


class SmartFrameApiClient:
    """Client for the Smart Frame local HTTP API."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        pin: str,
        timeout: int = 10,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self.base_url = base_url.rstrip("/")
        self._pin = pin
        self._timeout = ClientTimeout(total=timeout)

    async def async_get_status(self) -> dict[str, Any]:
        """Return the current Smart Frame status."""
        return await self._async_request("GET", "/api/status")

    async def async_get_current_image(self) -> bytes | None:
        """Return the currently displayed photo as JPEG bytes."""
        return await self._async_bytes_request("GET", "/current", allow_not_found=True)

    async def async_action(self, action: str, **params: Any) -> dict[str, Any]:
        """Send an action command to the Smart Frame."""
        data = {"action": action}
        data.update(
            {
                key: str(value).lower() if isinstance(value, bool) else value
                for key, value in params.items()
            }
        )
        return await self._async_request("POST", "/api/action", data=data)

    async def _async_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Send a JSON API request."""
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers["X-PhotoFrame-Pin"] = self._pin

        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            ) as response:
                if response.status == 401:
                    raise SmartFrameAuthError("invalid PIN")
                if response.status == 429:
                    raise SmartFrameRateLimited("too many failed PIN attempts")
                if response.status >= 400:
                    body = await response.text()
                    raise SmartFrameError(f"HTTP {response.status}: {body}")

                try:
                    payload = await response.json(content_type=None)
                except (ContentTypeError, ValueError) as err:
                    raise SmartFrameError("invalid JSON response") from err

        except (asyncio.TimeoutError, ClientError) as err:
            raise SmartFrameCannotConnect(str(err)) from err

        if not isinstance(payload, dict):
            raise SmartFrameError("unexpected JSON response")
        if payload.get("ok") is False:
            raise SmartFrameError(str(payload.get("error") or "request failed"))
        return payload

    async def _async_bytes_request(
        self,
        method: str,
        path: str,
        *,
        allow_not_found: bool = False,
        **kwargs: Any,
    ) -> bytes | None:
        """Send an API request that returns raw bytes."""
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers["X-PhotoFrame-Pin"] = self._pin

        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            ) as response:
                if allow_not_found and response.status == 404:
                    return None
                if response.status == 401:
                    raise SmartFrameAuthError("invalid PIN")
                if response.status == 429:
                    raise SmartFrameRateLimited("too many failed PIN attempts")
                if response.status >= 400:
                    body = await response.text()
                    raise SmartFrameError(f"HTTP {response.status}: {body}")
                return await response.read()
        except (asyncio.TimeoutError, ClientError) as err:
            raise SmartFrameCannotConnect(str(err)) from err
