from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import EMSCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    coordinator: EMSCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "domain": entry.domain,
            "title": entry.title,
            "options": dict(entry.options),
        },
        "data": coordinator.data or {},
        "house": coordinator.house.as_dict(),
        "decision": coordinator.decision.as_dict(),
    }
