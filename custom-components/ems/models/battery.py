"""
Battery model.

Representa el estado de la batería del sistema.

No conoce Home Assistant.
"""

from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class Battery:

    ####################################################################
    # Estado leído del inversor
    ####################################################################

    soc: float = 0.0
    power: float = 0.0
    voltage: float = 0.0
    current: float = 0.0

    ####################################################################
    # Configuración
    ####################################################################

    target_soc: float = 80.0
    full_soc: float = 95.0
    minimum_soc: float = 20.0

    ####################################################################
    # Gestión EMS
    ####################################################################

    reserved_power: float = 0.0
    available_power: float = 0.0
    charge_percentage: float = 100.0

    ####################################################################
    # Estado
    ####################################################################

    @property
    def charging(self) -> bool:
        return self.power < -50

    @property
    def discharging(self) -> bool:
        return self.power > 50

    @property
    def idle(self) -> bool:
        return abs(self.power) <= 50

    @property
    def full(self) -> bool:
        return self.soc >= self.full_soc

    @property
    def empty(self) -> bool:
        return self.soc <= self.minimum_soc

    @property
    def needs_charge(self) -> bool:
        return self.soc < self.target_soc

    @property
    def charge_ratio(self) -> float:
        return min(max(self.soc / self.full_soc, 0.0), 1.0)

    ####################################################################
    # EMS
    ####################################################################

    def reserve(self, watts: float) -> None:
        self.reserved_power = max(watts, 0)

    def set_available(self, watts: float) -> None:
        self.available_power = max(watts, 0)

    def set_charge_percentage(self, percentage: float) -> None:
        percentage = max(0, min(100, percentage))
        self.charge_percentage = percentage

    @property
    def target_charge_power(self) -> float:
        """
        Potencia que el EMS intentará reservar
        para cargar la batería.
        """
        return self.available_power * (
            self.charge_percentage / 100.0
        )

    @property
    def climate_budget(self) -> float:
        """
        Potencia restante disponible para climatización.
        """
        return max(
            self.available_power - self.target_charge_power,
            0,
        )

    ####################################################################
    # Información
    ####################################################################

    def as_dict(self) -> dict:
        return {
            "soc": self.soc,
            "power": self.power,
            "charging": self.charging,
            "discharging": self.discharging,
            "idle": self.idle,
            "full": self.full,
            "empty": self.empty,
            "target_soc": self.target_soc,
            "charge_percentage": self.charge_percentage,
            "target_charge_power": self.target_charge_power,
            "climate_budget": self.climate_budget,
        }

    ####################################################################
    # Debug
    ####################################################################

    def __str__(self):
        return (
            "Battery("
            f"soc={self.soc:.1f}%, "
            f"power={self.power:.0f}W, "
            f"target={self.target_soc:.0f}%, "
            f"charge_budget={self.target_charge_power:.0f}W, "
            f"climate_budget={self.climate_budget:.0f}W)"
        )