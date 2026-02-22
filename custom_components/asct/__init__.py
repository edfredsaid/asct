import asyncio
import logging
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components import persistent_notification
from .const import *
from .linear_regression import calculate_calibration

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})

    # --- BOOT-UP ABORT CHECK ---
    # If this flag is true on boot, it means HA restarted during a 24h cycle
    if entry.data.get("training_active"):
        persistent_notification.async_create(
            hass,
            f"Training for **{entry.title}** was aborted due to a Home Assistant restart. Please start it again from the configuration menu.",
            title="ASCT Training Aborted",
            notification_id=f"asct_abort_{entry.entry_id}"
        )
        # Reset the flag so it doesn't notify on every reboot
        new_data = dict(entry.data)
        new_data["training_active"] = False
        hass.config_entries.async_update_entry(entry, data=new_data)

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
        # Prevent starting a second training cycle if one is already running
        if self.entry.data.get("training_active"):
            return

        self.data_points = []
        nid = f"asct_{self.entry.entry_id}"

        # 1. Set the flag to True permanently in the config
        new_data = dict(self.entry.data)
        new_data["training_active"] = True
        self.hass.config_entries.async_update_entry(self.entry, data=new_data)

        # 2. Fire the updated Start notification
        persistent_notification.async_create(
            self.hass,
            f"Training started for **{self.entry.title}**. Keep sensors side-by-side for 24h.\n\n⚠️ **WARNING: Restarting Home Assistant will abort this training process.**",
            title="ASCT Training Active",
            notification_id=nid
        )

        unsub = async_track_state_change_event(
            self.hass,
            [self.entry.data[CONF_REFERENCE_SENSOR], self.entry.data[CONF_SOURCE_SENSOR]],
            self._handle_update
        )

        try:
            await asyncio.sleep(86400) # 24 Hour training window
        except asyncio.CancelledError:
            # Handle if the integration itself is reloaded or task cancelled
            unsub()
            return

        unsub()

        # 3. Calculate data
        m, b, health = calculate_calibration(self.data_points)

        # 4. Save calibration AND reset the active flag to False
        new_data = dict(self.entry.data)
        new_data["training_active"] = False
        new_data[CONF_MULTIPLIER] = m
        new_data[CONF_OFFSET] = b
        new_data[CONF_HEALTH] = health
        self.hass.config_entries.async_update_entry(self.entry, data=new_data)

        persistent_notification.async_dismiss(self.hass, nid)
        persistent_notification.async_create(
            self.hass,
            f"Training Complete for **{self.entry.title}**!\n\nConfidence: {health}%\nMultiplier: {m}\nOffset: {b}",
            title="ASCT Complete"
        )

    @callback
    def _handle_update(self, event):
        ref = self.hass.states.get(self.entry.data[CONF_REFERENCE_SENSOR])
        src = self.hass.states.get(self.entry.data[CONF_SOURCE_SENSOR])
        if ref and src and ref.state not in ['unknown', 'unavailable'] and src.state not in ['unknown', 'unavailable']:
            try:
                self.data_points.append((float(ref.state), float(src.state)))
            except ValueError: pass
