<img width="1000" height="400" alt="logo" src="https://github.com/user-attachments/assets/7c0f7892-d350-44fc-be41-2daf70601b0b" />

# Automated Sensor Calibration & Training (ASCT)

**ASCT** is a precision calibration engine for Home Assistant. It eliminates the problem of sensor reading variance by allowing high-variance devices (like IKEA Zigbee Lux sensors or uncalibrated thermometers) to "learn" from a trusted reference standard.

Unlike simple offsets, ASCT uses **Linear Regression** to calculate both the scaling (multiplier) and the baseline (offset) of a sensor, ensuring accuracy across the entire range of measurements.

---

## 🏗 How It Works

ASCT operates on a **Source** and **Reference** model:

1.  **Pairing:** You place a **Source Sensor** (the one you want to fix) physically adjacent to a **Reference Sensor** (your most accurate device).
2.  **Training Phase:** You trigger a 24-hour training cycle. ASCT collects data points in the background, capturing the natural fluctuations of the environment.
3.  **The Math:** ASCT performs a linear regression ($y = mx + b$) on the data, filtering out outliers (like temporary shadows or heat spikes) using standard deviation analysis.
4.  **The Output:** ASCT generates a new "Calibrated" entity (e.g., `sensor.kitchen_lux_calibrated`) that mirrors the behavior of the Reference sensor while using the hardware of the Source sensor.
5.  **Use:** You can now use your new calibrated entity anywhere just as any other sensor value.

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

## 🛠 Usage

### 1. Initial Setup
Go to **Settings > Devices & Services > Add Integration** and search for **ASCT**. Follow the UI prompts to select your Source and Reference sensors.

### 2. Start Training
1. Navigate to **Settings > Devices & Services**.
2. Find your **ASCT** integration card.
3. Click **Configure** (or the three dots `⋮` > Configure).
4. Check **Start 24h Training Now** and click **Submit**.
5.  **Wait 24 Hours.** Do not move or interfere with the sensors during this window.

### 3. Deployment
Once training is complete, you will receive a notification. You can now move the **Source Sensor** to its permanent location. The output entity created by ASCT will automatically apply the learned correction factor to all future readings.

## 📊 Why ASCT?

| Feature | Standard "Offset" | ASCT (Linear Regression) |
| :--- | :--- | :--- |
| **Baseline Correction** | ✅ Yes | ✅ Yes |
| **Scaling/Sensitivity** | ❌ No | ✅ Yes |
| **Outlier Rejection** | ❌ No | ✅ Yes |
| **Automation Friendly** | ❌ Manual | ✅ Automated |
