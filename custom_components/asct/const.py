"""Constants for the Automated Sensor Calibration & Training integration."""

DOMAIN = "asct"

# Configuration Keys (Data - Stored internally)
CONF_REFERENCE_SENSOR = "reference_sensor"
CONF_SOURCE_SENSOR = "source_sensor"
CONF_MULTIPLIER = "multiplier"
CONF_OFFSET = "offset"
CONF_HEALTH = "calibration_health"

# Configuration Keys (Options - User adjustable in UI)
CONF_FLOOR = "floor"
CONF_CEILING = "ceiling"
CONF_SMOOTHING = "smoothing"
CONF_DEADZONE = "deadzone"
CONF_LOGARITHMIC = "logarithmic"
CONF_THERMAL_LAG = "thermal_lag"
CONF_ALTITUDE = "altitude"
