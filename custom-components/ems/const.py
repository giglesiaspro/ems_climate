"""
Global constants for Smart EMS.

This module contains every constant used by the EMS.
Nothing outside this file should contain hardcoded values.
"""

from datetime import timedelta

###############################################################################
# GENERAL
###############################################################################

DOMAIN = "ems"

NAME = "Smart Energy Manager"

MANUFACTURER = "giglesiaspro"

VERSION = "0.1.0"

ATTRIBUTION = "Powered by Smart EMS"

###############################################################################
# UPDATE
###############################################################################

DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)

DEFAULT_HISTORY_SIZE = 100

###############################################################################
# LOGGER
###############################################################################

LOGGER_NAME = "custom_components.ems"

LOG_INFO = "INFO"

LOG_DEBUG = "DEBUG"

LOG_TRACE = "TRACE"

LOG_WARNING = "WARNING"

LOG_ERROR = "ERROR"

LOG_SUCCESS = "SUCCESS"

LOG_PLANNER = "PLANNER"

LOG_CLIMATE = "CLIMATE"

LOG_BATTERY = "BATTERY"

LOG_MANAGER = "MANAGER"

###############################################################################
# MODES
###############################################################################

MODE_OFF = "off"

MODE_SUMMER = "summer"

MODE_WINTER = "winter"

MODE_AUTO = "auto"

###############################################################################
# PRIORITIES
###############################################################################

PRIORITY_CRITICAL = 100

PRIORITY_HIGH = 75

PRIORITY_NORMAL = 50

PRIORITY_LOW = 25

###############################################################################
# BATTERY
###############################################################################

BATTERY_IDLE = "idle"

BATTERY_CHARGING = "charging"

BATTERY_DISCHARGING = "discharging"

BATTERY_FULL = "full"

###############################################################################
# CLIMATE
###############################################################################

CLIMATE_OFF = "off"

CLIMATE_RUNNING = "running"

CLIMATE_WAITING = "waiting"

###############################################################################
# DECISIONS
###############################################################################

DECISION_START = "start"

DECISION_STOP = "stop"

DECISION_KEEP = "keep"

DECISION_IGNORE = "ignore"

###############################################################################
# DEFAULT CONFIGURATION
###############################################################################

DEFAULT_BATTERY_TARGET = 70

DEFAULT_BATTERY_MIN_SOC = 20

DEFAULT_BATTERY_MAX_SOC = 95

DEFAULT_CLIMATE_DELAY = 30

DEFAULT_START_THRESHOLD = 600

DEFAULT_STOP_THRESHOLD = 200

DEFAULT_ROOM_TIMEOUT = 1800

###############################################################################
# SENSOR IDS
###############################################################################

SENSOR_PV_POWER = "sensor.solis_s6_eh1p_solax_pv_total_power"

SENSOR_HOUSE_LOAD = "sensor.solis_s6_eh1p_solax_bypass_load"

SENSOR_GRID_POWER = "sensor.solis_s6_eh1p_solax_meter_active_power"

SENSOR_BATTERY_POWER = "sensor.solis_s6_eh1p_solax_battery_power"

SENSOR_BATTERY_SOC = "sensor.solis_s6_eh1p_solax_battery_soc"

###############################################################################
# INPUT BOOLEANS
###############################################################################

INPUT_DEBUG = "input_boolean.energy_debug"

INPUT_SIMULATION = "input_boolean.energy_simulation"

INPUT_ENABLE = "input_boolean.energy_manager"

INPUT_SUMMER_MODE = (
    "input_boolean.modo_climatizacion_aire_on_calefaccion_off"
)

INPUT_SOLAR_MODE = "input_boolean.gas_o_sol"

INPUT_LOCK_CLIMATE = "input_boolean.no_cambiar_calefaccion"

INPUT_CLIMATE_AND_CHARGE = "input_boolean.climatizar_y_cargar"

###############################################################################
# INPUT NUMBERS
###############################################################################

INPUT_START_THRESHOLD = (
    "input_number.umbral_encendido_solar"
)

INPUT_BATTERY_TARGET = (
    "input_number.battery_target_percent"
)

INPUT_BATTERY_FULL = (
    "input_number.bateria_umbral_llena"
)

INPUT_DELAY = (
    "input_number.retardo_secuencial"
)

###############################################################################
# SERVICES
###############################################################################

SERVICE_RUN = "run"

SERVICE_PLAN = "plan"

SERVICE_STOP = "stop"

SERVICE_DIAGNOSTICS = "diagnostics"

###############################################################################
# EVENTS
###############################################################################

EVENT_PLANNER = "ems_planner"

EVENT_DECISION = "ems_decision"

EVENT_BATTERY = "ems_battery"

EVENT_CLIMATE = "ems_climate"

###############################################################################
# STORAGE
###############################################################################

STORAGE_VERSION = 1

STORAGE_KEY = "ems_statistics"

###############################################################################
# ROOMS
###############################################################################

ROOMS = (
    "ppal",
    "irati",
    "greta",
    "bruno",
    "buhardilla",
    "salon",
    "cocina",
)

###############################################################################
# DEBUG
###############################################################################

MAX_LOG_HISTORY = 500

MAX_DECISIONS = 500

MAX_STATISTICS = 5000