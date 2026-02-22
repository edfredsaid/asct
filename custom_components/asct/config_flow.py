import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN, CONF_REFERENCE_SENSOR, CONF_SOURCE_SENSOR,
    CONF_FLOOR, CONF_CEILING, CONF_SMOOTHING, CONF_DEADZONE,
    CONF_LOGARITHMIC, CONF_THERMAL_LAG, CONF_ALTITUDE
)

class ASCTFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            state = self.hass.states.get(user_input[CONF_SOURCE_SENSOR])
            name = state.name if state else "Calibrated Sensor"
            return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REFERENCE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ASCTOptionsFlowHandler(config_entry)


class ASCTOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        # FIX 1: Rename to avoid the reserved property collision!
        self.asct_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init",
            menu_options=["train_confirm", "settings_signal"]
        )

    async def async_step_train_confirm(self, user_input=None):
        if user_input is not None:
            if DOMAIN in self.hass.data and self.asct_entry.entry_id in self.hass.data[DOMAIN]:
                self.hass.async_create_task(
                    self.hass.data[DOMAIN][self.asct_entry.entry_id].start_training()
                )
            return self.async_create_entry(title="", data=self.asct_entry.options)

        return self.async_show_form(
            step_id="train_confirm",
            description_placeholders={"name": self.asct_entry.title}
        )

    async def async_step_settings_signal(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self.asct_entry.options

        data_schema = vol.Schema({
            vol.Optional(CONF_FLOOR, default=opts.get(CONF_FLOOR, 0.0)): vol.Coerce(float),
            vol.Optional(CONF_CEILING, default=opts.get(CONF_CEILING, 100000.0)): vol.Coerce(float),
            vol.Optional(CONF_LOGARITHMIC, default=opts.get(CONF_LOGARITHMIC, False)): bool,
            vol.Optional(CONF_SMOOTHING, default=opts.get(CONF_SMOOTHING, 0)): int,
            vol.Optional(CONF_DEADZONE, default=opts.get(CONF_DEADZONE, 1.0)): vol.Coerce(float),
            vol.Optional(CONF_THERMAL_LAG, default=opts.get(CONF_THERMAL_LAG, 0)): int,
            vol.Optional(CONF_ALTITUDE, default=opts.get(CONF_ALTITUDE, 0)): int,
        })

        return self.async_show_form(
            step_id="settings_signal",
            data_schema=data_schema
        )
