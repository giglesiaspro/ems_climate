from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_DECISION,
    INPUT_CLIMATE_AND_CHARGE,
    INPUT_ENABLE,
    INPUT_LOCK_CLIMATE,
    INPUT_SUMMER_MODE,
    LOGGER_NAME,
    SENSOR_BATTERY_POWER,
    SENSOR_BATTERY_SOC,
    SENSOR_GRID_POWER,
    SENSOR_HOUSE_LOAD,
    SENSOR_PV_POWER,
)
from .models.decision import Decision
from .models.house import House
from .models.planner import ClimatePlanner

_LOGGER = logging.getLogger(LOGGER_NAME)

UNKNOWN_STATES = {
    None,
    "",
    "unknown",
    "unavailable",
}


class EMSCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Main EMS polling coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.house = House()
        self.decision = Decision()
        self._planner = ClimatePlanner()

    async def _async_update_data(self) -> dict[str, Any]:
        self.house = self._build_house()
        self.decision = self._planner.plan(self.house)

        data = {
            "pv_power": self.house.energy.pv_power,
            "house_power": self.house.energy.house_power,
            "battery_power": self.house.energy.battery_power,
            "battery_soc": self.house.energy.battery_soc,
            "grid_power": self.house.energy.grid_power,
            "available_power": self.house.available_power,
            "planner_reason": self.decision.reason,
            "house": self.house.as_dict(),
            "decision": self.decision.as_dict(),
        }

        self.hass.bus.async_fire(
            EVENT_DECISION,
            self.decision.as_dict(),
        )

        return data

    def _build_house(self) -> House:
        house = House()

        house.energy.pv_power = self._state_float(SENSOR_PV_POWER)
        house.energy.house_power = self._state_float(SENSOR_HOUSE_LOAD)
        house.energy.battery_power = self._state_float(SENSOR_BATTERY_POWER)
        house.energy.battery_soc = self._state_float(SENSOR_BATTERY_SOC)
        house.energy.grid_power = self._state_float(SENSOR_GRID_POWER)

        house.battery.power = house.energy.battery_power
        house.battery.soc = house.energy.battery_soc

        house.summer_mode = self._state_bool(
            INPUT_SUMMER_MODE,
            default=True,
        )
        house.climate_enabled = (
            self._state_bool(INPUT_ENABLE, default=True)
            and not self._state_bool(INPUT_LOCK_CLIMATE, default=False)
        )
        house.climate_and_charge = self._state_bool(
            INPUT_CLIMATE_AND_CHARGE,
            default=False,
        )

        house.calculate_available_power()
        return house

    def _state_float(
        self,
        entity_id: str,
        default: float = 0.0,
    ) -> float:
        state = self.hass.states.get(entity_id)

        if state is None or state.state in UNKNOWN_STATES:
            return default

        try:
            return float(state.state)
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Invalid numeric state for %s: %s",
                entity_id,
                state.state,
            )
            return default

    def _state_bool(
        self,
        entity_id: str,
        default: bool,
    ) -> bool:
        state = self.hass.states.get(entity_id)

        if state is None or state.state in UNKNOWN_STATES:
            return default

        return state.state == "on"
