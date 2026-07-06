from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, NAME, ROOM_DEFINITIONS


class EMSConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Config flow for Smart EMS."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ):
        return EMSOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title=NAME,
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors={},
        )


class EMSOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Smart EMS."""

    def __init__(
        self,
        config_entry: config_entries.ConfigEntry,
    ) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict | None = None,
    ):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._schema(),
            errors={},
        )

    def _schema(self) -> vol.Schema:
        fields = {}

        for room_definition in ROOM_DEFINITIONS:
            room_id = room_definition["id"]
            fields[
                vol.Optional(
                    f"{room_id}_temperature_sensor",
                    default=self._option(
                        room_id,
                        "temperature_sensor",
                    ),
                    description={
                        "suggested_value": self._option(
                            room_id,
                            "temperature_sensor",
                        ),
                    },
                )
            ] = str
            fields[
                vol.Optional(
                    f"{room_id}_humidity_sensor",
                    default=self._option(
                        room_id,
                        "humidity_sensor",
                    ),
                    description={
                        "suggested_value": self._option(
                            room_id,
                            "humidity_sensor",
                        ),
                    },
                )
            ] = str
            fields[
                vol.Optional(
                    f"{room_id}_contact_sensor",
                    default=self._option(
                        room_id,
                        "contact_sensor",
                    ),
                    description={
                        "suggested_value": self._option(
                            room_id,
                            "contact_sensor",
                        ),
                    },
                )
            ] = str

        return vol.Schema(fields)

    def _option(
        self,
        room_id: str,
        field: str,
    ) -> str:
        value = self._config_entry.options.get(
            f"{room_id}_{field}",
            "",
        )
        return str(value)
