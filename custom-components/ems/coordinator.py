from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
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
    ROOM_CONTACT_ENTITY_PATTERNS,
    ROOM_DEFINITIONS,
    ROOM_HUMIDITY_ENTITY_PATTERNS,
    ROOM_TEMPERATURE_ENTITY_PATTERNS,
    SENSOR_BATTERY_POWER,
    SENSOR_BATTERY_SOC,
    SENSOR_GRID_POWER,
    SENSOR_HOUSE_LOAD,
    SENSOR_PV_POWER,
)
from .models.decision import Decision
from .models.house import House
from .models.planner import ClimatePlanner
from .models.room import Room

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
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.house = House()
        self.decision = Decision()
        self._entry = entry
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
            "room_count": self.house.room_count,
            "running_room_count": self.house.running_count,
            "rooms_needing_climate_count": len(
                self.house.rooms_needing_climate,
            ),
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

        house.rooms = [
            self._build_room(room_definition)
            for room_definition in ROOM_DEFINITIONS
        ]

        house.calculate_available_power()
        return house

    def _build_room(
        self,
        definition: dict[str, Any],
    ) -> Room:
        room_id = definition["id"]
        temperature_sensor = self._configured_room_entity(
            room_id,
            "temperature_sensor",
        ) or self._resolve_entity(
            ROOM_TEMPERATURE_ENTITY_PATTERNS,
            room_id,
        )
        humidity_sensor = self._configured_room_entity(
            room_id,
            "humidity_sensor",
        ) or self._resolve_entity(
            ROOM_HUMIDITY_ENTITY_PATTERNS,
            room_id,
        )
        contact_sensor = self._configured_room_entity(
            room_id,
            "contact_sensor",
        ) or self._resolve_entity(
            ROOM_CONTACT_ENTITY_PATTERNS,
            room_id,
        )

        temperature, has_temperature = self._optional_state_float(
            temperature_sensor,
        )
        humidity, _ = self._optional_state_float(
            humidity_sensor,
        )

        room = Room(
            id=room_id,
            name=definition["name"],
            priority=definition["priority"],
            temperature_sensor=temperature_sensor or "",
            humidity_sensor=humidity_sensor or "",
            contact_sensor=contact_sensor or "",
            available=has_temperature,
            temperature=temperature,
            humidity=humidity,
            target_summer=definition.get("target_summer", 25.0),
            target_winter=definition.get("target_winter", 21.0),
            hysteresis=definition.get("hysteresis", 0.5),
            startup_power=definition.get("startup_power", 900.0),
            maintenance_power=definition.get("maintenance_power", 450.0),
            conflict_group=definition.get("conflict_group"),
            incompatible_with=list(
                definition.get("incompatible_with", []),
            ),
        )

        room.synchronize(
            self._state_bool(
                contact_sensor,
                default=False,
            )
        )

        return room

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

    def _optional_state_float(
        self,
        entity_id: str | None,
    ) -> tuple[float, bool]:
        if entity_id is None:
            return 0.0, False

        state = self.hass.states.get(entity_id)

        if state is None or state.state in UNKNOWN_STATES:
            return 0.0, False

        try:
            return float(state.state), True
        except (TypeError, ValueError):
            _LOGGER.debug(
                "Invalid numeric state for %s: %s",
                entity_id,
                state.state,
            )
            return 0.0, False

    def _state_bool(
        self,
        entity_id: str | None,
        default: bool,
    ) -> bool:
        if entity_id is None:
            return default

        state = self.hass.states.get(entity_id)

        if state is None or state.state in UNKNOWN_STATES:
            return default

        return state.state == "on"

    def _resolve_entity(
        self,
        patterns: tuple[str, ...],
        room_id: str,
    ) -> str | None:
        for pattern in patterns:
            entity_id = pattern.format(room_id=room_id)
            if self.hass.states.get(entity_id) is not None:
                return entity_id

        return None

    def _configured_room_entity(
        self,
        room_id: str,
        field: str,
    ) -> str | None:
        entity_id = self._entry.options.get(
            f"{room_id}_{field}",
        )

        if not entity_id:
            return None

        return str(entity_id).strip() or None
