from homeassistant import config_entries
from homeassistant.helpers.selector import selector
import voluptuous as vol
from .const import *

# ==========================================
# Initial Setup Flow (Add Integration)
# ==========================================
class ASCTFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        # This step ID "user" matches strings.json -> config.step.user
        if user_input:
            state = self.hass.states.get(user_input[CONF_SOURCE_SENSOR])
            name = state.name if state else "Sensor"
            return self.async_create_entry(title=f"{name} Calibrated", data=user_input)

        # Using Native Selectors for the UI
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


# ==========================================
# Options Flow (Configure Button)
# ==========================================
class ASCTOptions(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    # --- The Main Menu ---
    async def async_step_init(self, user_input=None):
        # This step ID "init" matches strings.json -> options.step.init

        # The menu_options list matches the keys under options.step.init.menu_options
        return self.async_show_menu(
            step_id="init",
            menu_options=["train_confirm", "settings_signal"]
        )

    # --- Sub-Step 1: Confirmation Dialog ---
    async def async_step_train_confirm(self, user_input=None):
        # This step ID "train_confirm" matches strings.json -> options.step.train_confirm
        if user_input is not None:
            self.hass.async_create_task(
                self.hass.data[DOMAIN][self.entry.entry_id].start_training()
            )
            return self.async_create_entry(title="", data={})

        # We pass the sensor name so the string can use placeholder {name}
        return self.async_show_form(
            step_id="train_confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"name": self.entry.title}
        )

    # --- Sub-Step 2: Settings Form ---
    async def async_step_settings_signal(self, user_input=None):
        # This step ID "settings_signal" matches strings.json -> options.step.settings_signal
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self.entry.options

        # The constants here (e.g., CONF_FLOOR which is "floor") match the
        # keys under options.step.settings_signal.data_description in the JSON
        schema = vol.Schema({
            vol.Optional(CONF_FLOOR, default=opts.get(CONF_FLOOR, 0.0)): vol.Coerce(float),
            vol.Optional(CONF_CEILING, default=opts.get(CONF_CEILING, 100000.0)): vol.Coerce(float),
            vol.Optional(CONF_LOGARITHMIC, default=opts.get(CONF_LOGARITHMIC, False)): bool,
            vol.Optional(CONF_SMOOTHING, default=opts.get(CONF_SMOOTHING, 0)): int,
            vol.Optional(CONF_DEADZONE, default=opts.get(CONF_DEADZONE, 1.0)): vol.Coerce(float),
            vol.Optional(CONF_THERMAL_LAG, default=opts.get(CONF_THERMAL_LAG, 0)): int,
            vol.Optional(CONF_ALTITUDE, default=opts.get(CONF_ALTITUDE, 0)): int,
        })

        return self.async_show_form(step_id="settings_signal", data_schema=schema)
