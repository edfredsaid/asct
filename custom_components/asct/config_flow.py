from homeassistant import config_entries
from homeassistant.helpers.selector import selector
import voluptuous as vol
from .const import *

class ASCTFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            state = self.hass.states.get(user_input[CONF_SOURCE_SENSOR])
            name = state.name if state else "Sensor"
            return self.async_create_entry(title=f"{name} Calibrated", data=user_input)

        # This creates the native search/picker UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REFERENCE_SENSOR): selector({
                    "entity": {"domain": "sensor"}
                }),
                vol.Required(CONF_SOURCE_SENSOR): selector({
                    "entity": {"domain": "sensor"}
                }),
            })
        )

    @staticmethod
    def async_get_options_flow(entry):
        return ASCTOptions(entry)

class ASCTOptions(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input:
            if user_input.get("train"):
                self.hass.async_create_task(
                    self.hass.data[DOMAIN][self.entry.entry_id].start_training()
                )
            return self.async_create_entry(title="", data=user_input)

        opts = self.entry.options
        # We can also use selectors for the numeric fields to add sliders/limits!
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("train", default=False): bool,
                vol.Optional(CONF_FLOOR, default=opts.get(CONF_FLOOR, 0.0)): vol.Coerce(float),
                vol.Optional(CONF_CEILING, default=opts.get(CONF_CEILING, 100000.0)): vol.Coerce(float),
                vol.Optional(CONF_SMOOTHING, default=opts.get(CONF_SMOOTHING, 0)): int,
                vol.Optional(CONF_DEADZONE, default=opts.get(CONF_DEADZONE, 1.0)): vol.Coerce(float),
                vol.Optional(CONF_LOGARITHMIC, default=opts.get(CONF_LOGARITHMIC, False)): bool,
                vol.Optional(CONF_THERMAL_LAG, default=opts.get(CONF_THERMAL_LAG, 0)): int,
                vol.Optional(CONF_ALTITUDE, default=opts.get(CONF_ALTITUDE, 0)): int,
            })
        )
