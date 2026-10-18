"""Config flow for EV-ES Cloud."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EvesCloudApiError, EvesCloudAuthenticationError, EvesCloudClient, EvesCloudSubscriptionError
from .const import CONF_BASE_URL, CONF_EMAIL, CONF_PASSWORD, CONF_TOKEN, DEFAULT_BASE_URL, DOMAIN


class EvesCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle EV-ES Cloud setup and reauthentication."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            base_url = str(user_input[CONF_BASE_URL]).rstrip("/")
            email = str(user_input[CONF_EMAIL]).strip().lower()
            # Check before requesting a new token. Cloud intentionally permits
            # only one active HA token per account, so a duplicate setup must
            # never invalidate the token used by an existing entry.
            await self.async_set_unique_id(f"eves_cloud_{email}")
            self._abort_if_unique_id_configured()
            client = EvesCloudClient(async_get_clientsession(self.hass), base_url)
            try:
                response = await client.async_login(email, str(user_input[CONF_PASSWORD]))
            except EvesCloudAuthenticationError:
                errors["base"] = "invalid_auth"
            except EvesCloudSubscriptionError:
                errors["base"] = "subscription_required"
            except EvesCloudApiError:
                errors["base"] = "cannot_connect"
            else:
                token = response.get("token")
                if not isinstance(token, str) or token == "":
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=f"EV-ES Cloud ({email})",
                        data={CONF_BASE_URL: base_url, CONF_EMAIL: email, CONF_TOKEN: token},
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, entry_data):
        """Start token renewal after the Cloud rejects it."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Use the Cloud password once to issue a replacement token."""
        errors = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            client = EvesCloudClient(async_get_clientsession(self.hass), str(entry.data[CONF_BASE_URL]))
            try:
                response = await client.async_login(str(entry.data[CONF_EMAIL]), str(user_input[CONF_PASSWORD]))
            except EvesCloudAuthenticationError:
                errors["base"] = "invalid_auth"
            except EvesCloudSubscriptionError:
                errors["base"] = "subscription_required"
            except EvesCloudApiError:
                errors["base"] = "cannot_connect"
            else:
                token = response.get("token")
                if isinstance(token, str) and token:
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates={CONF_TOKEN: token},
                        reason="reauth_successful",
                    )
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )
