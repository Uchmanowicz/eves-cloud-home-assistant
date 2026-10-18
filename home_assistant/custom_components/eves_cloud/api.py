"""HTTPS client for the read-only EV-ES Cloud Home Assistant API."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession


class EvesCloudApiError(Exception):
    """Base API communication error."""


class EvesCloudAuthenticationError(EvesCloudApiError):
    """The Cloud password or token is no longer accepted."""


class EvesCloudSubscriptionError(EvesCloudApiError):
    """The Cloud account has no active subscription."""


class EvesCloudClient:
    """Read latest EV-BPM telemetry from EV-ES Cloud."""

    def __init__(self, session: ClientSession, base_url: str, token: str | None = None) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._token = token

    @property
    def endpoint(self) -> str:
        return f"{self._base_url}/home-assistant-api.php"

    async def async_login(self, email: str, password: str) -> dict[str, Any]:
        """Exchange an account password for a scoped, revocable API token."""
        return await self._request("POST", json={"email": email, "password": password})

    async def async_get_devices(self) -> dict[str, Any]:
        """Read all devices assigned to the Cloud account."""
        if not self._token:
            raise EvesCloudAuthenticationError("Missing EV-ES Cloud token")
        return await self._request("GET")

    async def _request(self, method: str, **kwargs: Any) -> dict[str, Any]:
        headers = {"Accept": "application/json", "User-Agent": "HomeAssistant-EVES-Cloud/0.1"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        try:
            async with self._session.request(method, self.endpoint, headers=headers, timeout=20, **kwargs) as response:
                try:
                    body = await response.json(content_type=None)
                except (ValueError, ClientError) as err:
                    raise EvesCloudApiError("Cloud returned an invalid response") from err
        except ClientError as err:
            raise EvesCloudApiError("Could not connect to EV-ES Cloud") from err

        if response.status == 401:
            raise EvesCloudAuthenticationError("Cloud rejected credentials or token")
        if response.status == 403:
            raise EvesCloudSubscriptionError("Cloud subscription is inactive")
        if response.status == 429:
            raise EvesCloudApiError("Cloud sign-in is temporarily rate limited")
        if response.status >= 400 or not isinstance(body, dict) or body.get("ok") is not True:
            raise EvesCloudApiError(f"Cloud API error: HTTP {response.status}")
        return body
