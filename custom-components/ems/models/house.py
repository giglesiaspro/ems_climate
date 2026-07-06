"""
House model.

Representa el estado completo de la vivienda.

Este será el objeto principal utilizado por el Planner.

No conoce Home Assistant.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from .battery import Battery
from .energy import Energy
from .room import Room


@dataclass(slots=True)
class House:

    ###########################################################################
    # Modelos principales
    ###########################################################################

    energy: Energy = field(default_factory=Energy)
    battery: Battery = field(default_factory=Battery)
    rooms: list[Room] = field(default_factory=list)

    ###########################################################################
    # Configuración
    ###########################################################################

    summer_mode: bool = True
    eco_mode: bool = False
    climate_enabled: bool = True
    battery_enabled: bool = True
    climate_and_charge: bool = False

    ###########################################################################
    # Planner
    ###########################################################################

    available_power: float = 0.0
    reserved_power: float = 0.0
    planner_reason: str = ""

    ###########################################################################
    # Habitaciones
    ###########################################################################

    def room(self, room_id: str) -> Room | None:
        for room in self.rooms:
            if room.id == room_id:
                return room
        return None

    ###########################################################################
    # Estados
    ###########################################################################

    @property
    def running_rooms(self) -> list[Room]:
        return [
            room
            for room in self.rooms
            if room.running
        ]

    @property
    def stopped_rooms(self) -> list[Room]:

        return [
            room
            for room in self.rooms
            if not room.running
        ]

    @property
    def enabled_rooms(self) -> list[Room]:

        return [
            room
            for room in self.rooms
            if room.enabled
        ]

    @property
    def rooms_needing_climate(self) -> list[Room]:
        return [
            room
            for room in self.enabled_rooms
            if room.needs_climate(self.summer_mode)
        ]

    ###########################################################################
    # Potencias
    ###########################################################################

    @property
    def startup_power(self) -> float:
        return sum(
            room.startup_power
            for room in self.running_rooms
        )

    @property
    def maintenance_power(self) -> float:
        return sum(
            room.maintenance_power
            for room in self.running_rooms
        )

    ###########################################################################
    # Planner
    ###########################################################################

    def calculate_available_power(self):
        self.available_power = self.energy.available_climate_power
        return self.available_power

    ###########################################################################
    # Estadísticas
    ###########################################################################

    @property
    def room_count(self):
        return len(self.rooms)

    @property
    def running_count(self):
        return len(self.running_rooms)

    ###########################################################################
    # Serialización
    ###########################################################################

    def as_dict(self):
        return {
            "summer_mode": self.summer_mode,
            "eco_mode": self.eco_mode,
            "climate_enabled": self.climate_enabled,
            "battery_enabled": self.battery_enabled,
            "climate_and_charge": self.climate_and_charge,
            "available_power": self.available_power,
            "energy": self.energy.as_dict(),
            "battery": self.battery.as_dict(),
            "rooms": [
                room.as_dict()
                for room in self.rooms
            ]
        }

    ###########################################################################
    # Debug
    ###########################################################################

    def __str__(self):
        return (
            "House("
            f"rooms={self.room_count}, "
            f"running={self.running_count}, "
            f"surplus={self.energy.surplus:.0f}W, "
            f"soc={self.battery.soc:.0f}%)"
        )
