"""
Decision model.

Representa la decisión tomada por el Planner.

Este objeto será consumido por el Executor.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from .room import Room

@dataclass(slots=True)
class Decision:

    ###########################################################################
    # Fecha
    ###########################################################################

    timestamp: datetime = field(default_factory=datetime.now)

    ###########################################################################
    # Habitaciones
    ###########################################################################

    start_rooms: list[Room] = field(default_factory=list)
    stop_rooms: list[Room] = field(default_factory=list)
    keep_rooms: list[Room] = field(default_factory=list)

    ###########################################################################
    # Planner
    ###########################################################################

    score: float = 0.0
    reason: str = ""

    ###########################################################################
    # Energía
    ###########################################################################

    available_power: float = 0.0
    climate_power: float = 0.0
    battery_power: float = 0.0

    ###########################################################################
    # Estado
    ###########################################################################

    success: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    ###########################################################################
    # Planner
    ###########################################################################

    iterations: int = 0
    elapsed_ms: float = 0.0

    ###########################################################################
    # Helpers
    ###########################################################################

    @property
    def has_changes(self) -> bool:
        return bool(self.start_rooms or self.stop_rooms)

    @property
    def is_empty(self) -> bool:
        return (
            len(self.start_rooms) == 0
            and len(self.stop_rooms) == 0
        )

    ###########################################################################
    # Potencia
    ###########################################################################

    @property
    def required_start_power(self) -> float:
        return sum(
            room.startup_power
            for room in self.start_rooms
        )

    @property
    def required_maintenance_power(self) -> float:
        rooms = self.start_rooms + self.keep_rooms
        return sum(
            room.maintenance_power
            for room in rooms
        )

    ###########################################################################
    # Gestión
    ###########################################################################

    def add_start(self, room: Room):
        if room not in self.start_rooms:
            self.start_rooms.append(room)

    def add_stop(self, room: Room):
        if room not in self.stop_rooms:
            self.stop_rooms.append(room)

    def add_keep(self, room: Room):
        if room not in self.keep_rooms:
            self.keep_rooms.append(room)

    ###########################################################################
    # Logs
    ###########################################################################

    def warning(self, message: str):
        self.warnings.append(message)

    def error(self, message: str):
        self.errors.append(message)
        self.success = False

    ###########################################################################
    # Resumen
    ###########################################################################

    @property
    def summary(self):
        return {
            "start": [
                room.name
                for room in self.start_rooms
            ],
            "stop": [
                room.name
                for room in self.stop_rooms
            ],
            "keep": [
                room.name
                for room in self.keep_rooms
            ],
            "score": self.score,
            "reason": self.reason,
            "battery_power": self.battery_power,
            "climate_power": self.climate_power,

        }

    ###########################################################################
    # Serialización
    ###########################################################################

    def as_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "reason": self.reason,
            "start_rooms": [
                room.id
                for room in self.start_rooms
            ],
            "stop_rooms": [
                room.id
                for room in self.stop_rooms
            ],
            "keep_rooms": [
                room.id
                for room in self.keep_rooms
            ],
            "battery_power": self.battery_power,
            "climate_power": self.climate_power,
            "available_power": self.available_power,
            "warnings": self.warnings,
            "errors": self.errors,
            "iterations": self.iterations,
            "elapsed_ms": self.elapsed_ms,
        }

    ###########################################################################
    # Debug
    ###########################################################################

    def __str__(self):
        return (
            "Decision("
            f"start={len(self.start_rooms)}, "
            f"stop={len(self.stop_rooms)}, "
            f"keep={len(self.keep_rooms)}, "
            f"score={self.score:.1f}, "
            f"battery={self.battery_power:.0f}W, "
            f"climate={self.climate_power:.0f}W)"
        )