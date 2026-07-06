from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, NAME
from .coordinator import EMSCoordinator


@dataclass(frozen=True, kw_only=True)
class EMSSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[EMSSensorDescription, ...] = (
    EMSSensorDescription(
        key="pv_power",
        translation_key="pv_power",
        name="PV Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pv_power"),
    ),
    EMSSensorDescription(
        key="house_power",
        translation_key="house_power",
        name="House Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("house_power"),
    ),
    EMSSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        name="Grid Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("grid_power"),
    ),
    EMSSensorDescription(
        key="battery_power",
        translation_key="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery_power"),
    ),
    EMSSensorDescription(
        key="battery_soc",
        translation_key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery_soc"),
    ),
    EMSSensorDescription(
        key="available_power",
        translation_key="available_power",
        name="Available Climate Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("available_power"),
    ),
    EMSSensorDescription(
        key="planner_reason",
        translation_key="planner_reason",
        name="Planner Reason",
        value_fn=lambda data: data.get("planner_reason"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EMSCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        EMSSensor(coordinator, entry, description)
        for description in SENSORS
    )


class EMSSensor(CoordinatorEntity[EMSCoordinator], SensorEntity):
    entity_description: EMSSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EMSCoordinator,
        entry: ConfigEntry,
        description: EMSSensorDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, entry.entry_id),
            },
            "name": NAME,
            "manufacturer": MANUFACTURER,
        }

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(
            self.coordinator.data or {},
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.key != "planner_reason":
            return None

        data = self.coordinator.data or {}
        decision = data.get("decision", {})

        return {
            "start_rooms": decision.get("start_rooms", []),
            "stop_rooms": decision.get("stop_rooms", []),
            "keep_rooms": decision.get("keep_rooms", []),
            "climate_power": decision.get("climate_power", 0),
            "battery_power": decision.get("battery_power", 0),
            "elapsed_ms": decision.get("elapsed_ms", 0),
        }
