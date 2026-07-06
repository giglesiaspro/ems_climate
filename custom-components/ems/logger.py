"""
EMS Logger

Centralized logger for the Energy Management System.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

from homeassistant.core import HomeAssistant

from .const import LOGGER_NAME

_LOGGER = logging.getLogger(LOGGER_NAME)


class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    PLANNER = "PLANNER"
    BATTERY = "BATTERY"
    CLIMATE = "CLIMATE"
    MANAGER = "MANAGER"


@dataclass(slots=True)
class LogEntry:
    timestamp: datetime
    level: LogLevel
    source: str
    message: str


class EMSLogger:

    def __init__(
        self,
        hass: HomeAssistant,
        history_size: int = 500,
    ):

        self._hass = hass

        self._history = deque(maxlen=history_size)

        self.debug_enabled = False

        self.telegram_enabled = False

        self.persistent_enabled = False

    ####################################################################
    # PUBLIC API
    ####################################################################

    def trace(self, source: str, message: str):

        self._write(LogLevel.TRACE, source, message)

    def debug(self, source: str, message: str):

        if self.debug_enabled:

            self._write(LogLevel.DEBUG, source, message)

    def info(self, source: str, message: str):

        self._write(LogLevel.INFO, source, message)

    def success(self, source: str, message: str):

        self._write(LogLevel.SUCCESS, source, message)

    def warning(self, source: str, message: str):

        self._write(LogLevel.WARNING, source, message)

    def error(self, source: str, message: str):

        self._write(LogLevel.ERROR, source, message)

    def planner(self, message: str):

        self._write(LogLevel.PLANNER, "planner", message)

    def battery(self, message: str):

        self._write(LogLevel.BATTERY, "battery", message)

    def climate(self, message: str):

        self._write(LogLevel.CLIMATE, "climate", message)

    def manager(self, message: str):

        self._write(LogLevel.MANAGER, "manager", message)

    ####################################################################
    # HISTORY
    ####################################################################

    @property
    def history(self):

        return list(self._history)

    def last(self):

        if not self._history:

            return None

        return self._history[-1]

    ####################################################################
    # INTERNAL
    ####################################################################

    def _write(
        self,
        level: LogLevel,
        source: str,
        message: str,
    ):

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            source=source,
            message=message,
        )

        self._history.append(entry)

        formatted = (
            f"[{level.value}] "
            f"[{source}] "
            f"{message}"
        )

        if level == LogLevel.ERROR:

            _LOGGER.error(formatted)

        elif level == LogLevel.WARNING:

            _LOGGER.warning(formatted)

        else:

            _LOGGER.info(formatted)

        self._fire_event(entry)

        self._persistent_notification(entry)

        self._telegram(entry)

    ####################################################################
    # EVENTS
    ####################################################################

    def _fire_event(
        self,
        entry: LogEntry,
    ):

        self._hass.bus.fire(
            "ems_log",
            {
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level.value,
                "source": entry.source,
                "message": entry.message,
            },
        )

    ####################################################################
    # TELEGRAM
    ####################################################################

    def _telegram(
        self,
        entry: LogEntry,
    ):

        if not self.telegram_enabled:

            return

        try:

            self._hass.services.call(

                "telegram_bot",

                "send_message",

                {
                    "message":
                        f"[{entry.level.value}] "
                        f"{entry.source}\n"
                        f"{entry.message}"
                },

                blocking=False,

            )

        except Exception as ex:

            _LOGGER.error(
                "Telegram logger error: %s",
                ex,
            )

    ####################################################################
    # PERSISTENT
    ####################################################################

    def _persistent_notification(
        self,
        entry: LogEntry,
    ):

        if not self.persistent_enabled:

            return

        try:

            self._hass.services.call(

                "persistent_notification",

                "create",

                {
                    "title": f"EMS {entry.level.value}",

                    "message": entry.message,

                },

                blocking=False,

            )

        except Exception as ex:

            _LOGGER.error(
                "Persistent notification error: %s",
                ex,
            )