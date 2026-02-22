import math
from collections import deque
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.event import async_track_state_change_event
from .const import *

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([CalibratedSensor(hass, entry)])

class CalibratedSensor(SensorEntity):
    # FIX 2: Strict Enum usage for modern HA
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry = entry
        self._source_id = entry.data[CONF_SOURCE_SENSOR]
        self._attr_name = entry.title
        self._attr_unique_id = f"asct_cal_{entry.entry_id}"
        self._samples = deque()
        self._last_val = None

        source_state = hass.states.get(self._source_id)
        if source_state:
            self._attr_native_unit_of_measurement = source_state.attributes.get("unit_of_measurement")
            self._attr_device_class = source_state.attributes.get("device_class")

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_track_state_change_event(self.hass, self._source_id, self._update_state)
        )

        current_state = self.hass.states.get(self._source_id)
        if current_state and current_state.state not in ["unknown", "unavailable"]:
            class FakeEvent:
                data = {"new_state": current_state}
            await self._update_state(FakeEvent())

    async def _update_state(self, event):
        new_state = event.data.get("new_state")
        if not new_state or new_state.state in ["unknown", "unavailable"]: return

        try:
            val = float(new_state.state)
            opts = self._entry.options

            if (win := opts.get(CONF_SMOOTHING, 0)) > 0:
                self._samples.append(val)
                if len(self._samples) > max(1, int(win/30)): self._samples.popleft()
                val = sum(self._samples)/len(self._samples)

            m, b = self._entry.data.get(CONF_MULTIPLIER, 1.0), self._entry.data.get(CONF_OFFSET, 0.0)
            val = (val * m) + b

            if (lag := opts.get(CONF_THERMAL_LAG, 0)) > 0 and self._last_val:
                val = val + ((val - self._last_val) * (lag / 60))

            if opts.get(CONF_LOGARITHMIC):
                val = math.log1p(max(0, val)) * (val / (math.log1p(val) or 1))

            val = max(opts.get(CONF_FLOOR, -9999), min(val, opts.get(CONF_CEILING, 999999)))

            if self._last_val and abs(val - self._last_val) < (self._last_val * (opts.get(CONF_DEADZONE, 0)/100)):
                return

            self._attr_native_value = round(val, 2)
            self._attr_extra_state_attributes = {"health_score": f"{self._entry.data.get(CONF_HEALTH, 0)}%"}
            self._last_val = val
            self.async_write_ha_state()
        except ValueError: pass
