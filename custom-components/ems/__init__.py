from homeassistant.config_entries import ConfigEntry

from homeassistant.const import Platform

from homeassistant.core import HomeAssistant

from .const import DOMAIN

from .coordinator import EMSCoordinator

PLATFORMS = [
    Platform.SENSOR,
]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
):

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):

    coordinator = EMSCoordinator(hass)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass,
    entry,
):

    await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    hass.data[DOMAIN].pop(
        entry.entry_id,
    )

    return True
