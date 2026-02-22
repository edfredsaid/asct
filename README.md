<img width="1000" height="400" alt="logo" src="https://github.com/user-attachments/assets/7c0f7892-d350-44fc-be41-2daf70601b0b" />

# Automated Sensor Calibration & Training (ASCT)

**ASCT** is a precision calibration engine for Home Assistant. It mitigates against the problem of sensor variance by allowing high-variance devices (like IKEA Zigbee Lux sensors or uncalibrated thermometers) to "learn" from a trusted reference standard.

Unlike simple offsets, ASCT uses **Linear Regression** to calculate both the scaling (multiplier) and the baseline (offset) of a sensor, ensuring accuracy across the entire range of measurements.

---

## 🚀 Installation

### Via HACS (Recommended)
1.  Open **HACS** in Home Assistant.
2.  Click the three dots in the top right and select **Custom Repositories**.
3.  Add the URL of this repository and select **Integration** as the category.
4.  Click **Install**.
5.  Restart Home Assistant.

### Manual Installation
1.  Download the `asct` folder from this repository.
2.  Copy it into your Home Assistant `custom_components/` directory.
3.  Restart Home Assistant.

---

## How It Works

1. **Pair Sensors:** Go to **Settings > Devices & Services > Add Integration**, search for Automated Sensor Calibration & Training, and select your Source (inaccurate) and Reference (accurate) sensors.
2. **Start Training:** Click **Configure** on the new integration and select **Start 24h Training Cycle**.
3. **Wait:** Leave the two sensors physically next to each other for 24 hours. The integration will silently collect data points every time they change.
4. **Enjoy:** After 24 hours, the math is applied, and your new calibrated sensor will accurately mirror the reference environment!

---

### ⚠️ Important: Training Interruption
The training process runs entirely in Home Assistant's active memory for exactly 24 hours. 
**Restarting Home Assistant while a training cycle is active will permanently abort the training.** If this happens, you will receive a notification warning you that the training was aborted. You will need to start the process again from the Configuration menu.

---

## 🛠️ Configuration & Signal Processing

Once your sensor is paired (or even after it is trained), you can click **Configure** on the integration to access advanced signal processing settings. These settings change how your sensor behaves *after* the calibration math is applied.

* **Minimum Value Floor:** The sensor will never report a value lower than this number. Useful for sensors that drop to 0 too early.
* **Maximum Value Ceiling:** The sensor will never report a value higher than this number. Useful for clamping humidity at 100%.
* **Use Logarithmic Scaling:** Recommended for Lux/Illuminance sensors. This makes low-light changes more perceptible, matching human vision.
* **Smoothing Window (Seconds):** Averages readings over time to remove sudden, noisy spikes (e.g., a bird flying over a solar sensor, or a draft hitting a thermostat). Set to `0` to disable.
* **Deadzone Hysteresis (%):** The sensor will ignore tiny fluctuations smaller than this percentage. This prevents noisy, constant updates from flooding your Home Assistant database.
* **Thermal Lag Compensation (Seconds):** Designed for slow-to-respond temperature sensors (e.g., those enclosed in thick plastic cases). It calculates the rate of change to predict and report the real temperature ahead of time.
* **Altitude Offset (Meters):** For pressure sensors only. Adjusts the reading to Mean Sea Level (MSL) based on your current physical elevation.

---

## 📊 Calibration Confidence (Health Score)

When the 24-hour training completes, ASCT calculates an R² correlation score, representing how closely the source sensor tracks the reference sensor. 

To keep your entity list clean, this percentage is stored as a hidden **Attribute** on your calibrated sensor rather than a separate entity. 

**How to view your Confidence Score:**
1. Click on your calibrated sensor in any dashboard.
2. Expand the **Attributes** dropdown in the More Info pop-up.
3. Look for `health_score`.

**How to display it on a dashboard:**
You can easily extract this attribute using a standard entities card in your Lovelace dashboard:

```yaml
type: entities
entities:
  - type: attribute
    entity: sensor.your_calibrated_sensor
    attribute: health_score
    name: Calibration Confidence
    icon: mdi:percent
```

## 📊 Why ASCT?

| Feature | Standard "Offset" | ASCT (Linear Regression) |
| :--- | :--- | :--- |
| **Baseline Correction** | ✅ Yes | ✅ Yes |
| **Scaling/Sensitivity** | ❌ No | ✅ Yes |
| **Outlier Rejection** | ❌ No | ✅ Yes |
| **Automation Friendly** | ❌ Manual | ✅ Automated |
