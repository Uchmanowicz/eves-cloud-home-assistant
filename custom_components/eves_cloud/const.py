"""Constants for the EV-ES Cloud integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "eves_cloud"
DEFAULT_BASE_URL = "https://ev-es.pl/Cloud"
CONF_BASE_URL = "base_url"
CONF_EMAIL = "email"
CONF_TOKEN = "token"
CONF_PASSWORD = "password"
PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "select", "button"]
UPDATE_INTERVAL = timedelta(seconds=15)
