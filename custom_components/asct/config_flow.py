from homeassistant import config_entries
import voluptuous as vol
from .const import *

class ASCTFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input:
            state = self.hass.states.get(user_input[CONF_SOURCE_SENSOR])
            name = state.name if state else "Sensor"
            return self.async_create_entry(title=f"{name} Calibrated", data=user_input)
        sensors = {s.entity_id: f"{s.name} ({s.entity_id})" for s in self.hass.states.async_all() if s.domain == "sensor"}
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required(CONF_REFERENCE_SENSOR): vol.In(sensors),
            vol.Required(CONF_SOURCE_SENSOR): vol.In(sensors),
        }))

    @staticmethod
    def async_get_options_flow(entry): return ASCTOptions(entry)

class ASCTOptions(config_entries.OptionsFlow):
    def __init__(self, entry): self.entry = entry
    async def async_step_init(self, user_input=None):
        if user_input:
            if user_input.get("train"):
                self.hass.async_create_task(self.hass.data[DOMAIN][self.entry.entry_id].start_training())
            return self.async_create_entry(title="", data=user_input)
        opts = self.entry.options
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Optional("train", default=False): bool,
            vol.Optional(CONF_FLOOR, default=opts.get(CONF_FLOOR, 0.0)): vol.Coerce(float),
            vol.Optional(CONF_CEILING, default=opts.get(CONF_CEILING, 100000.0)): vol.Coerce(float),
            vol.Optional(CONF_SMOOTHING, default=opts.get(CONF_SMOOTHING, 0)): int,
            vol.Optional(CONF_DEADZONE, default=opts.get(CONF_DEADZONE, 1.0)): vol.Coerce(float),
            vol.Optional(CONF_LOGARITHMIC, default=opts.get(CONF_LOGARITHMIC, False)): bool,
            vol.Optional(CONF_THERMAL_LAG, default=opts.get(CONF_THERMAL_LAG, 0)): int,
            vol.Optional(CONF_ALTITUDE, default=opts.get(CONF_ALTITUDE, 0)): int,
        }))
