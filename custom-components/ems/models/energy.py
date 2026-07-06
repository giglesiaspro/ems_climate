"""
Energy model.
Representa el estado energético completo de la vivienda en un instante.
NO conoce Home Assistant.
NO conoce sensores.
Simplemente almacena información energética.
"""

from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class Energy:

    ###########################################################################
    # Producción solar
    ###########################################################################

    pv_power: float = 0.0

    ###########################################################################
    # Consumo vivienda
    ###########################################################################

    house_power: float = 0.0

    ###########################################################################
    # Potencia batería
    #
    #  >0 descargando
    #  <0 cargando
    ###########################################################################

    battery_power: float = 0.0

    ###########################################################################
    # Estado batería
    ###########################################################################

    battery_soc: float = 0.0

    ###########################################################################
    # Potencia red
    #
    # >0 exportando
    # <0 importando
    ###########################################################################

    grid_power: float = 0.0

    ###########################################################################
    # Propiedades calculadas
    ###########################################################################

    @property
    def exporting(self) -> bool:
        return self.grid_power > 0

    @property
    def importing(self) -> bool:
        return self.grid_power < 0

    @property
    def battery_charging(self) -> bool:
        return self.battery_power < 0

    @property
    def battery_discharging(self) -> bool:
        return self.battery_power > 0

    @property
    def battery_idle(self) -> bool:
        return abs(self.battery_power) < 20

    @property
    def surplus(self) -> float:
        """
        Excedente REAL disponible.

        Si estamos importando energía
        devuelve siempre 0.
        """
        return max(self.grid_power, 0)

    @property
    def deficit(self) -> float:
        """
        Potencia que estamos comprando.
        """
        return abs(min(self.grid_power, 0))

    @property
    def available_climate_power(self) -> float:
        """
        Potencia disponible para climatización.

        En esta primera versión coincide con el excedente.
        En futuras versiones el BatteryManager podrá reservar
        parte de esta potencia.
        """
        return self.surplus

    @property
    def net_house_consumption(self) -> float:
        """
        Consumo instantáneo de la vivienda.
        """
        return self.house_power

    @property
    def self_consumption(self) -> float:
        """
        Energía solar aprovechada directamente.
        """
        return min(
            self.house_power,
            self.pv_power,
        )

    @property
    def pv_unused(self) -> float:
        """
        Producción solar que no está siendo utilizada.

        No es exactamente igual al excedente cuando exista
        batería cargando.
        """
        unused = self.pv_power - self.self_consumption

        if unused < 0:
            return 0

        return unused

    ###########################################################################
    # Estado resumido
    ###########################################################################

    @property
    def status(self) -> str:

        if self.importing:
            return "IMPORTING"
        if self.exporting:
            return "EXPORTING"
        return "BALANCED"

    ###########################################################################
    # Conversión
    ###########################################################################

    def as_dict(self) -> dict:

        return {
            "pv_power": self.pv_power,
            "house_power": self.house_power,
            "battery_power": self.battery_power,
            "battery_soc": self.battery_soc,
            "grid_power": self.grid_power,
            "surplus": self.surplus,
            "deficit": self.deficit,
            "exporting": self.exporting,
            "importing": self.importing,
            "battery_charging": self.battery_charging,
            "battery_discharging": self.battery_discharging,
            "available_climate_power": self.available_climate_power,
        }

    ###########################################################################
    # Debug
    ###########################################################################

    def __str__(self) -> str:

        return (

            "Energy("
            f"pv={self.pv_power:.0f}W, "
            f"house={self.house_power:.0f}W, "
            f"battery={self.battery_power:.0f}W, "
            f"soc={self.battery_soc:.1f}%, "
            f"grid={self.grid_power:.0f}W, "
            f"surplus={self.surplus:.0f}W)"
        )