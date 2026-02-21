import asyncio
import logging
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from .const import *
from .linear_regression import calculate_calibration

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    coordinator = ASCTCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

class ASCTCoordinator:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.data_points = []

    async def start_training(self):
        self.data_points = []
        nid = f"asct_{self.entry.entry_id}"
        self.hass.components.persistent_notification.async_create(
            f"Training started for {self.entry.title}. Keep sensors side-by-side for 24h.",
            "ASCT Training Active", nid
        )

        unsub = async_track_state_change_event(
            self.hass, [self.entry.data[CONF_REFERENCE_SENSOR], self.entry.data[CONF_SOURCE_SENSOR]],
            self._handle_update
        )

        await asyncio.sleep(86400)
        unsub()

        m, b, health = calculate_calibration(self.data_points)
        self.hass.config_entries.async_update_entry(
            self.entry, data={**self.entry.data, CONF_MULTIPLIER: m, CONF_OFFSET: b, CONF_HEALTH: health}
        )

        self.hass.components.persistent_notification.async_dismiss(nid)
        self.hass.components.persistent_notification.async_create(
            f"Training Complete for {self.entry.title}!\n\nConfidence: {health}%\nMultiplier: {m}\nOffset: {b}",
            "ASCT Complete"
        )

    @callback
    def _handle_update(self, event):
        ref = self.hass.states.get(self.entry.data[CONF_REFERENCE_SENSOR])
        src = self.hass.states.get(self.entry.data[CONF_SOURCE_SENSOR])
        if ref and src and ref.state not in ['unknown', 'unavailable'] and src.state not in ['unknown', 'unavailable']:
            try:
                self.data_points.append((float(ref.state), float(src.state)))
            except ValueError: pass
