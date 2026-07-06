from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import DOMAIN


class EMSCoordinator(DataUpdateCoordinator):

    def __init__(self, hass):

        super().__init__(

            hass,

            logger=None,

            name=DOMAIN,

            update_interval=timedelta(
                seconds=10,
            ),

        )

    async def _async_update_data(self):

        return {
            "pv_power": float(
                self.hass.states.get(
                    "sensor.solis_s6_eh1p_solax_pv_total_power"
                ).state
            ),

            "house_power": float(
                self.hass.states.get(
                    "sensor.solis_s6_eh1p_solax_bypass_load"
                ).state
            ),

            "battery_power": float(
                self.hass.states.get(
                    "sensor.solis_s6_eh1p_solax_battery_power"
                ).state
            ),

            "battery_soc": float(
                self.hass.states.get(
                    "sensor.solis_s6_eh1p_solax_battery_soc"
                ).state
            ),

            "grid_power": float(
                self.hass.states.get(
                    "sensor.solis_s6_eh1p_solax_meter_active_power"
                ).state
            ),

        }