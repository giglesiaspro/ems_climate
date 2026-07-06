"""
Statistics model.

Almacena estadísticas persistentes del EMS para que el sistema
aprenda el comportamiento de la vivienda.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(slots=True)
class Statistics:

    ###########################################################################
    # Planner
    ###########################################################################

    planner_runs: int = 0
    successful_plans: int = 0
    failed_plans: int = 0
    average_score: float = 0.0
    average_time_ms: float = 0.0

    ###########################################################################
    # Climatización
    ###########################################################################

    climate_starts: int = 0
    climate_stops: int = 0
    climate_runtime_minutes: int = 0

    ###########################################################################
    # Energía
    ###########################################################################

    solar_used_kwh: float = 0.0
    solar_exported_kwh: float = 0.0
    imported_kwh: float = 0.0
    battery_charged_kwh: float = 0.0
    battery_discharged_kwh: float = 0.0

    ###########################################################################
    # Aprendizaje
    ###########################################################################

    learning_cycles: int = 0
    learned_rooms: int = 0

    ###########################################################################
    # Histórico
    ###########################################################################

    last_execution: datetime | None = None
    last_learning: datetime | None = None

    ###########################################################################
    # Planner
    ###########################################################################

    def register_plan(
        self,
        success: bool,
        score: float,
        elapsed_ms: float,
    ):
        self.planner_runs += 1
        self.last_execution = datetime.now()
        if success:
            self.successful_plans += 1
        else:
            self.failed_plans += 1
        if self.planner_runs == 1:
            self.average_score = score
            self.average_time_ms = elapsed_ms
            return
        alpha = 0.10
        self.average_score = (
            self.average_score * (1 - alpha)
            +
            score * alpha
        )

        self.average_time_ms = (
            self.average_time_ms * (1 - alpha)
            +
            elapsed_ms * alpha
        )

    ###########################################################################
    # Climatización
    ###########################################################################

    def register_start(self):
        self.climate_starts += 1

    def register_stop(self):
        self.climate_stops += 1

    ###########################################################################
    # Aprendizaje
    ###########################################################################

    def register_learning(self):
        self.learning_cycles += 1
        self.last_learning = datetime.now()

    ###########################################################################
    # Energía
    ###########################################################################

    def add_import(self, kwh: float):
        self.imported_kwh += kwh

    def add_export(self, kwh: float):
        self.solar_exported_kwh += kwh

    def add_self_consumption(self, kwh: float):
        self.solar_used_kwh += kwh

    def add_battery_charge(self, kwh: float):
        self.battery_charged_kwh += kwh

    def add_battery_discharge(self, kwh: float):
        self.battery_discharged_kwh += kwh

    ###########################################################################
    # Métricas
    ###########################################################################

    @property
    def planner_success_rate(self) -> float:
        if self.planner_runs == 0:
            return 0.0
        return (
            self.successful_plans
            / self.planner_runs
        ) * 100.0

    ###########################################################################
    # Exportación
    ###########################################################################

    def as_dict(self):
        return {
            "planner_runs": self.planner_runs,
            "successful_plans": self.successful_plans,
            "failed_plans": self.failed_plans,
            "planner_success_rate": self.planner_success_rate,
            "average_score": self.average_score,
            "average_time_ms": self.average_time_ms,
            "climate_starts": self.climate_starts,
            "climate_stops": self.climate_stops,
            "climate_runtime_minutes": self.climate_runtime_minutes,
            "solar_used_kwh": self.solar_used_kwh,
            "solar_exported_kwh": self.solar_exported_kwh,
            "imported_kwh": self.imported_kwh,
            "battery_charged_kwh": self.battery_charged_kwh,
            "battery_discharged_kwh": self.battery_discharged_kwh,
            "learning_cycles": self.learning_cycles,
            "learned_rooms": self.learned_rooms,
        }

    ###########################################################################
    # Debug
    ###########################################################################

    def __str__(self):
        return (
            "Statistics("
            f"plans={self.planner_runs}, "
            f"success={self.planner_success_rate:.1f}%, "
            f"score={self.average_score:.1f})"
        )