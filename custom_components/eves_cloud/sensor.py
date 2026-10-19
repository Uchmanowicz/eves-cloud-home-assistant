"""Sensor entities for EV-ES Cloud."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower, UnitOfTemperature
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity

SENSORS: tuple[tuple[str, str, str | None, Callable[[dict[str, Any]], Any]], ...] = (
    ("soc", "State of charge", PERCENTAGE, lambda data: data.get("soc")),
    ("soh", "State of health", PERCENTAGE, lambda data: data.get("soh")),
    ("power", "Power", UnitOfPower.KILO_WATT, lambda data: data.get("power")),
    ("current", "Current", UnitOfElectricCurrent.AMPERE, lambda data: data.get("current")),
    ("pack_voltage", "Pack voltage", UnitOfElectricPotential.VOLT, lambda data: data.get("pack_voltage")),
    ("cell_voltage_min", "Minimum cell voltage", UnitOfElectricPotential.VOLT, lambda data: data.get("cell_voltage_min")),
    ("cell_voltage_average", "Average cell voltage", UnitOfElectricPotential.VOLT, lambda data: data.get("cell_voltage_average")),
    ("cell_voltage_max", "Maximum cell voltage", UnitOfElectricPotential.VOLT, lambda data: data.get("cell_voltage_max")),
    ("cell_voltage_delta_mv", "Cell voltage delta", "mV", lambda data: data.get("cell_voltage_delta_mv")),
    ("cell_voltage_min_limit", "Minimum cell voltage limit", UnitOfElectricPotential.VOLT, lambda data: data.get("cell_voltage_min_limit")),
    ("cell_voltage_max_limit", "Maximum cell voltage limit", UnitOfElectricPotential.VOLT, lambda data: data.get("cell_voltage_max_limit")),
    ("global_minimum_cell_id", "Global minimum cell ID", None, lambda data: data.get("global_minimum_cell_id")),
    ("global_maximum_cell_id", "Global maximum cell ID", None, lambda data: data.get("global_maximum_cell_id")),
    ("temperature_min", "Minimum temperature", UnitOfTemperature.CELSIUS, lambda data: data.get("temperature_min")),
    ("temperature_average", "Average temperature", UnitOfTemperature.CELSIUS, lambda data: data.get("temperature_average")),
    ("temperature_max", "Maximum temperature", UnitOfTemperature.CELSIUS, lambda data: data.get("temperature_max")),
    ("cycle_count", "Cycle count", None, lambda data: data.get("cycle_count")),
    ("charge_current_limit", "Charge current limit", UnitOfElectricCurrent.AMPERE, lambda data: data.get("charge_current_limit")),
    ("discharge_current_limit", "Discharge current limit", UnitOfElectricCurrent.AMPERE, lambda data: data.get("discharge_current_limit")),
    ("contactor_pwm", "Contactor PWM", None, lambda data: data.get("contactor_pwm")),
    ("local_ip_address", "Local IP address", None, lambda data: data.get("local_ip_address")),
    ("firmware_version", "Firmware version", None, lambda data: data.get("firmware_version")),
    ("battery_state", "Battery state", None, lambda data: data.get("battery_state")),
    ("device_state", "Device state", None, lambda data: data.get("device_state")),
    ("active_error_count", "Active error count", None, lambda data: len(data.get("active_errors") or [])),
    ("last_error_count", "Last error count", None, lambda data: len(data.get("last_errors") or [])),
)


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add all current EV-BPM sensor entities."""
    coordinator = entry.runtime_data.coordinator
    entities = [
        EvesCloudSensor(coordinator, serial, key, name, unit, value_getter)
        for serial in coordinator.data
        for key, name, unit, value_getter in SENSORS
    ]
    entities.extend(EvesCloudTechnicalDiagnosticsSensor(coordinator, serial) for serial in coordinator.data)
    async_add_entities(entities)


class EvesCloudSensor(EvesCloudEntity, SensorEntity):
    """One numeric or state sensor from the latest Cloud update."""

    def __init__(self, coordinator, serial: str, key: str, name: str, unit: str | None, value_getter) -> None:
        super().__init__(coordinator, serial)
        self._key = key
        self._value_getter = value_getter
        self._attr_translation_key = None
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{serial}_{key}"

    @property
    def native_value(self):
        data = self.device_data
        return self._value_getter(data) if data is not None else None


class EvesCloudTechnicalDiagnosticsSensor(EvesCloudEntity, SensorEntity):
    """Expose the compact device diagnostic report without a long HA state."""

    _attr_name = "Technical diagnostics"
    _attr_icon = "mdi:memory"

    def __init__(self, coordinator, serial: str) -> None:
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_technical_diagnostics"

    @property
    def native_value(self) -> str | None:
        data = self.device_data
        return "Available" if data and data.get("technical_diagnostics") else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.device_data or {}
        return {"report": data.get("technical_diagnostics")}
