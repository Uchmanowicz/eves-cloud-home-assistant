"""Number entities for EV-ES Cloud battery configuration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity


NUMBER_CONTROLS = (
    ("max_charge_current", "Maximum charge current", "config_max_charge_current_a", "max_charge_current_a", 0, 300, 1, "A", False),
    ("max_discharge_current", "Maximum discharge current", "config_max_discharge_current_a", "max_discharge_current_a", 0, 300, 1, "A", False),
    ("max_cell_delta", "Maximum cell delta", "config_max_cell_delta_mv", "max_cell_delta_mv", 0, 2000, 1, "mV", False),
    ("balance_min_voltage", "Balance minimum voltage", "config_balance_min_voltage_v", "balance_min_voltage_v", 3, 5, 0.001, "V", True),
    ("balance_voltage_hysteresis", "Balance voltage hysteresis", "config_balance_voltage_hysteresis_mv", "balance_voltage_hysteresis_mv", 0, 600, 1, "mV", True),
)


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add configurable EV-BPM values."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EvesCloudNumber(coordinator, serial, control)
        for serial in coordinator.data
        for control in NUMBER_CONTROLS
    )


class EvesCloudNumber(EvesCloudEntity, NumberEntity):
    """One persisted EV-BPM configuration number."""

    def __init__(self, coordinator, serial: str, control) -> None:
        super().__init__(coordinator, serial)
        key, name, data_key, change_key, minimum, maximum, step, unit, requires_balancing = control
        self._data_key = data_key
        self._change_key = change_key
        self._requires_balancing = requires_balancing
        self._attr_unique_id = f"{serial}_{key}_control"
        self._attr_name = name
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX

    @property
    def available(self) -> bool:
        data = self.device_data
        if not super().available or not data or data.get("online") is not True:
            return False
        if data.get("is_owner") is not True or data.get(self._data_key) is None:
            return False
        return not self._requires_balancing or (
            data.get("config_can_balance") is True and data.get("config_balancing_enabled") is True
        )

    @property
    def native_value(self) -> float | None:
        data = self.device_data
        value = data.get(self._data_key) if data else None
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Queue the full configuration with one changed value."""
        normalized = round(value, 3) if self._attr_native_step < 1 else int(round(value))
        await self.async_queue_command("configuration.update", changes={self._change_key: normalized})
