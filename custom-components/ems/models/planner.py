"""
Climate planner.

Convierte el estado de la vivienda en una decisión de climatización.

No conoce Home Assistant.
"""

from __future__ import annotations

from time import perf_counter

from .decision import Decision
from .house import House
from .room import Room


class ClimatePlanner:
    """
    Planner determinista para una primera versión del EMS.

    La estrategia es conservadora:
    - Mantiene habitaciones encendidas si siguen necesitando clima.
    - Para habitaciones que ya no necesitan clima, si respetan tiempo mínimo.
    - Arranca habitaciones candidatas por puntuación y presupuesto.
    """

    def plan(
        self,
        house: House,
    ) -> Decision:
        started_at = perf_counter()

        decision = Decision(
            available_power=house.calculate_available_power(),
        )

        if not house.climate_enabled:
            self._stop_all_possible(
                house,
                decision,
                "climate disabled",
            )
            self._finish(decision, started_at, "climate disabled")
            return decision

        budget = decision.available_power
        selected_rooms: list[Room] = []

        for room in house.enabled_rooms:
            if room.running and room.needs_climate(house.summer_mode):
                decision.add_keep(room)
                selected_rooms.append(room)
                budget -= room.maintenance_power
                room.set_score(
                    self._score_room(room, house.summer_mode),
                    "already running",
                )

        self._select_stops(house, decision)

        for room in self._start_candidates(house):
            decision.iterations += 1

            score = self._score_room(room, house.summer_mode)
            room.set_score(score, "candidate")

            if not room.can_start():
                room.set_score(score, "minimum off time")
                continue

            if self._conflicts_with_any(room, selected_rooms):
                room.set_score(score, "conflict")
                continue

            if room.startup_power > budget:
                room.set_score(score, "not enough surplus")
                continue

            decision.add_start(room)
            selected_rooms.append(room)
            budget -= room.startup_power
            room.set_score(score, "selected")

        decision.climate_power = sum(
            room.maintenance_power
            for room in decision.keep_rooms
        ) + sum(
            room.startup_power
            for room in decision.start_rooms
        )

        decision.battery_power = max(
            decision.available_power - decision.climate_power,
            0,
        )

        self._finish(
            decision,
            started_at,
            self._reason(decision),
        )

        return decision

    def _select_stops(
        self,
        house: House,
        decision: Decision,
    ) -> None:
        for room in house.running_rooms:
            if room.enabled and room.needs_climate(house.summer_mode):
                continue

            if room.can_stop():
                decision.add_stop(room)
                room.set_score(0.0, "stop requested")
            else:
                decision.add_keep(room)
                room.set_score(0.0, "minimum on time")

    def _stop_all_possible(
        self,
        house: House,
        decision: Decision,
        reason: str,
    ) -> None:
        for room in house.running_rooms:
            if room.can_stop():
                decision.add_stop(room)
                room.set_score(0.0, reason)
            else:
                decision.add_keep(room)
                room.set_score(0.0, "minimum on time")

    def _start_candidates(
        self,
        house: House,
    ) -> list[Room]:
        candidates = [
            room
            for room in house.rooms_needing_climate
            if not room.running
            and room.available
        ]
        return sorted(
            candidates,
            key=lambda room: self._score_room(
                room,
                house.summer_mode,
            ),
            reverse=True,
        )

    def _score_room(
        self,
        room: Room,
        summer_mode: bool,
    ) -> float:
        return (
            room.priority
            + max(room.delta(summer_mode), 0.0) * 100.0
        )

    def _conflicts_with_any(
        self,
        room: Room,
        selected_rooms: list[Room],
    ) -> bool:
        return any(
            room.conflicts_with(selected_room)
            for selected_room in selected_rooms
        )

    def _reason(
        self,
        decision: Decision,
    ) -> str:
        if decision.start_rooms:
            return "start selected rooms"
        if decision.stop_rooms:
            return "stop satisfied rooms"
        if decision.keep_rooms:
            return "keep current rooms"
        return "no climate action"

    def _finish(
        self,
        decision: Decision,
        started_at: float,
        reason: str,
    ) -> None:
        decision.reason = reason
        decision.elapsed_ms = (
            perf_counter() - started_at
        ) * 1000.0
