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

        # Native Entity Picker UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_REFERENCE_SENSOR): selector({"entity": {"domain": "sensor"}}),
                vol.Required(CONF_SOURCE_SENSOR): selector({"entity": {"domain": "sensor"}}),
            })
        )

    @staticmethod
    def async_get_options_flow(entry):
        return ASCTOptions(entry)

class ASCTOptions(config_entries.OptionsFlow):
    """The modernized, menu-driven options flow."""
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Present the main menu choice."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["train_confirm", "settings_signal"]
        )

    async def async_step_train_confirm(self, user_input=None):
        """Confirm starting the training action."""
        if user_input is not None:
            # Trigger training in the background
            self.hass.async_create_task(
                self.hass.data[DOMAIN][self.entry.entry_id].start_training()
            )
            # Close the flow immediately
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="train_confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"name": self.entry.title}
        )

    async def async_step_settings_signal(self, user_input=None):
        """The main settings form organized by sections."""
        if user_input is not None:
            # Save settings
            return self.async_create_entry(title="", data=user_input)

        opts = self.entry.options

        # Using data_description strings instead of sections for wider compatibility
        # while keeping visual separation clear through ordering.
        schema = vol.Schema({
            # --- Section: Limits ---
            vol.Optional(CONF_FLOOR, default=opts.get(CONF_FLOOR, 0.0)): vol.Coerce(float),
            vol.Optional(CONF_CEILING, default=opts.get(CONF_CEILING, 100000.0)): vol.Coerce(float),
            vol.Optional(CONF_LOGARITHMIC, default=opts.get(CONF_LOGARITHMIC, False)): bool,

            # --- Section: Noise Reduction ---
            vol.Optional(CONF_SMOOTHING, default=opts.get(CONF_SMOOTHING, 0)): int,
            vol.Optional(CONF_DEADZONE, default=opts.get(CONF_DEADZONE, 1.0)): vol.Coerce(float),

            # --- Section: Environmental ---
            vol.Optional(CONF_THERMAL_LAG, default=opts.get(CONF_THERMAL_LAG, 0)): int,
            vol.Optional(CONF_ALTITUDE, default=opts.get(CONF_ALTITUDE, 0)): int,
        })

        return self.async_show_form(step_id="settings_signal", data_schema=schema)
