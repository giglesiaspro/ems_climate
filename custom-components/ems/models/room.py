"""
Room model.

Representa una habitación climatizable.

No conoce Home Assistant.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass(slots=True)
class Room:
    """
    Modelo completo de una habitación.

    Toda la lógica del Planner trabajará sobre este objeto.
    """

    ###########################################################################
    # Identificación
    ###########################################################################

    id: str
    name: str

    ###########################################################################
    # Configuración
    ###########################################################################

    priority: int = 50
    enabled: bool = True

    ###########################################################################
    # Sensores
    ###########################################################################

    temperature_sensor: str = ""
    humidity_sensor: str = ""
    contact_sensor: str = ""

    ###########################################################################
    # Estado detectado
    ###########################################################################

    detected_on: bool = False
    commanded_on: bool = False
    available: bool = True

    ###########################################################################
    # Variables ambientales
    ###########################################################################

    temperature: float = 0.0
    humidity: float = 0.0

    ###########################################################################
    # Objetivos
    ###########################################################################

    target_summer: float = 25.0
    target_winter: float = 21.0
    hysteresis: float = 0.5

    ###########################################################################
    # Potencias aprendidas
    ###########################################################################

    startup_power: float = 900.0
    maintenance_power: float = 450.0
    startup_samples: int = 0
    maintenance_samples: int = 0

    ###########################################################################
    # Aprendizaje térmico
    ###########################################################################

    cooling_speed: float = 0.12
    heating_speed: float = 0.08

    ###########################################################################
    # Historial temperatura
    ###########################################################################

    previous_temperature: float = 0.0
    temperature_rate: float = 0.0

    ###########################################################################
    # Restricciones
    ###########################################################################

    minimum_on_time: int = 300
    minimum_off_time: int = 180

    ###########################################################################
    # Incompatibilidades
    ###########################################################################

    conflict_group: str | None = None
    incompatible_with: list[str] = field(default_factory=list)

    ###########################################################################
    # Estadísticas
    ###########################################################################

    starts: int = 0
    stops: int = 0
    runtime_minutes: int = 0
    total_energy_kwh: float = 0.0

    ###########################################################################
    # Planner
    ###########################################################################

    planner_score: float = 0.0
    planner_reason: str = ""

    ###########################################################################
    # Tiempos
    ###########################################################################

    last_start: datetime | None = None
    last_stop: datetime | None = None

    ###########################################################################
    # Estado
    ###########################################################################

    @property
    def running(self) -> bool:
        """
        Estado REAL del split.
        Se obtiene del sensor de contacto.
        """
        return self.detected_on

    @property
    def synchronized(self) -> bool:
        """
        True cuando lo que cree el EMS coincide con el estado real.
        """
        return self.commanded_on == self.detected_on

    @property
    def desynchronized(self) -> bool:
        """
        El usuario ha utilizado el mando o ha ocurrido un error.
        """
        return not self.synchronized

    ###########################################################################
    # Temperatura objetivo
    ###########################################################################

    def target_temperature(
        self,
        summer_mode: bool,
    ) -> float:

        if summer_mode:
            return self.target_summer
        return self.target_winter

    ###########################################################################
    # Necesidad térmica
    ###########################################################################

    def delta(
        self,
        summer_mode: bool,
    ) -> float:

        if summer_mode:
            return self.temperature - self.target_summer
        return self.target_winter - self.temperature

    def needs_climate(
        self,
        summer_mode: bool,
    ) -> bool:

        if not self.available:
            return False

        return self.delta(summer_mode) > self.hysteresis

    def needs_cooling(self) -> bool:
        return self.needs_climate(
            summer_mode=True,
        )

    def needs_heating(self) -> bool:
        return self.needs_climate(
            summer_mode=False,
        )

    ###########################################################################
    # Restricciones de arranque
    ###########################################################################

    def can_start(self) -> bool:
        if self.running:
            return False
        if self.last_stop is None:
            return True
        return (
            datetime.now() - self.last_stop
        ) >= timedelta(seconds=self.minimum_off_time)

    def can_stop(self) -> bool:
        if not self.running:
            return False
        if self.last_start is None:
            return True
        return (
            datetime.now() - self.last_start
        ) >= timedelta(seconds=self.minimum_on_time)

    ###########################################################################
    # Aprendizaje de potencia
    ###########################################################################

    def learn_startup_power(
        self,
        measured_power: float,
    ) -> None:
        """
        Aprende la potencia real de arranque usando una media móvil.
        """
        if measured_power <= 0:
            return
        alpha = 0.15
        if self.startup_samples == 0:
            self.startup_power = measured_power
        else:
            self.startup_power = (
                (1 - alpha) * self.startup_power
                + alpha * measured_power
            )
        self.startup_samples += 1

    def learn_maintenance_power(
        self,
        measured_power: float,
    ) -> None:
        """
        Aprende la potencia de mantenimiento.
        """
        if measured_power <= 0:
            return
        alpha = 0.10
        if self.maintenance_samples == 0:
            self.maintenance_power = measured_power
        else:
            self.maintenance_power = (
                (1 - alpha) * self.maintenance_power
                + alpha * measured_power
            )
        self.maintenance_samples += 1

    ###########################################################################
    # Aprendizaje térmico
    ###########################################################################

    def learn_temperature_rate(
        self,
        new_temperature: float,
        elapsed_minutes: float,
    ) -> None:
        """
        Aprende la velocidad de calentamiento/enfriamiento.
        """
        if elapsed_minutes <= 0:
            return
        variation = abs(
            new_temperature - self.previous_temperature
        )
        rate = variation / elapsed_minutes
        alpha = 0.10
        if new_temperature < self.previous_temperature:
            self.cooling_speed = (
                (1 - alpha) * self.cooling_speed
                + alpha * rate
            )
        else:
            self.heating_speed = (
                (1 - alpha) * self.heating_speed
                + alpha * rate
            )
        self.temperature_rate = rate
        self.previous_temperature = new_temperature

    ###########################################################################
    # Planner
    ###########################################################################

    def set_score(
        self,
        score: float,
        reason: str,
    ) -> None:
        self.planner_score = score
        self.planner_reason = reason

    ###########################################################################
    # Compatibilidad
    ###########################################################################

    def conflicts_with(
        self,
        other: "Room",
    ) -> bool:
        """
        Comprueba si dos habitaciones son incompatibles.
        """
        if other.id in self.incompatible_with:
            return True
        if self.id in other.incompatible_with:
            return True
        if (
            self.conflict_group
            and self.conflict_group == other.conflict_group
            and self.id != other.id
        ):
            return True
        return False

    ###########################################################################
    # Ciclo de vida
    ###########################################################################

    def started(self) -> None:
        self.commanded_on = True
        self.last_start = datetime.now()
        self.starts += 1

    def stopped(self) -> None:
        self.commanded_on = False
        self.last_stop = datetime.now()
        self.stops += 1

    ###########################################################################
    # Sincronización
    ###########################################################################

    def synchronize(
        self,
        detected_state: bool,
    ) -> None:
        """
        Actualiza el estado detectado por el sensor de contacto.
        """
        self.detected_on = detected_state

    ###########################################################################
    # Estadísticas
    ###########################################################################

    def add_runtime(
        self,
        minutes: float,
    ) -> None:
        if minutes <= 0:
            return
        self.runtime_minutes += int(minutes)

    def add_energy(
        self,
        kwh: float,
    ) -> None:
        if kwh <= 0:
            return
        self.total_energy_kwh += kwh

    ###########################################################################
    # Exportación
    ###########################################################################

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "enabled": self.enabled,
            "running": self.running,
            "commanded_on": self.commanded_on,
            "detected_on": self.detected_on,
            "desynchronized": self.desynchronized,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "target_summer": self.target_summer,
            "target_winter": self.target_winter,
            "startup_power": round(self.startup_power, 1),
            "maintenance_power": round(
                self.maintenance_power,
                1,
            ),

            "cooling_speed": round(
                self.cooling_speed,
                3,
            ),
            "heating_speed": round(
                self.heating_speed,
                3,
            ),
            "starts": self.starts,
            "stops": self.stops,
            "runtime_minutes": self.runtime_minutes,
            "total_energy_kwh": round(
                self.total_energy_kwh,
                3,
            ),
            "planner_score": self.planner_score,
            "planner_reason": self.planner_reason,
        }

    ###########################################################################
    # Debug
    ###########################################################################

    def __str__(self) -> str:
        return (
            f"{self.name} | "
            f"T={self.temperature:.1f}° | "
            f"Target={self.target_summer:.1f}/{self.target_winter:.1f}° | "
            f"Running={self.running} | "
            f"Cmd={self.commanded_on} | "
            f"Detected={self.detected_on} | "
            f"Score={self.planner_score:.1f}"
        )
