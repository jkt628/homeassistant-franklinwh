# FranklinWH Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)

This is a modern custom integration for [Home Assistant](https://www.home-assistant.io/) that provides comprehensive monitoring and control for FranklinWH home energy storage systems.

> ⚠️ This project is unofficial and not affiliated with FranklinWH.

______________________________________________________________________

## 📝 About This Fork

Based on complete rewrite by Joshua Seidel ([@JoshuaSeidel](https://github.com/JoshuaSeidel)) with Anthropic Claude Sonnet 4.5.\
Originally inspired by [@richo](https://github.com/richo)'s [homeassistant-franklinwh](https://github.com/richo/homeassistant-franklinwh).\
[Extended](https://github.com/jkt628/homeassistant-franklinwh) by [@jkt628](https://github.com/jkt628) with support for multiple installations and new controls for Mode, Reserve, SmartCircuits, _etc._\
Uses [@jkt628](https://github.com/jkt628)'s fork of [franklinwh-python](https://github.com/jkt628/franklinwh-python) library.

______________________________________________________________________

## ✨ Features

### Accessories

Additional sensors and controls become available depending on an installation's accessories and configuration.

- ⚡ [Generator Module](https://www.franklinwh.com/accessories/generator-module/) production and energy insights
- 🎛️ [Smart Circuits Module](https://www.franklinwh.com/accessories/smart-circuits/) monitoring and control

### Monitoring

- 📊 Live battery status (State of Charge, charging/discharging power)
- ☀️ Solar production and energy generation tracking
- 🔌 Grid import/export monitoring with totals
- 🏠 Home load power monitoring and total energy consumption

### Control

- ⚙️ Operation mode selection (self_use, backup, time_of_use)
- 🔋 Battery reserve setting
- 🌐 Grid connection control

### Modern Features

- 🎨 **Config Flow**: Easy setup through the Home Assistant UI
- 🏘️ **Multiple Installation**: Individual controls for each FranklinWH installation
- 🔄 **DataUpdateCoordinator**: Efficient polling with minimal API calls
- 📱 **Device Registry**: All entities grouped under one device per installation
- 🔍 **Diagnostics**: Built-in debugging support
- 🌐 **Local API Support**: Experimental local communication (when available)
- 🛠️ **Services**: Custom services for advanced control

______________________________________________________________________

## 📦 Installation

### Via HACS (Recommended)

1. In Home Assistant, go to **HACS → Integrations**.
1. Click the menu (⋮) → **Custom repositories**.
1. Add this repository URL: <https://github.com/jkt628/homeassistant-franklinwh>
1. Choose category **Integration** and click **Add**.
1. Search for **FranklinWH** in HACS and click **Download**.
1. Restart Home Assistant.

### Manual Installation

1. Download this repository as a ZIP file.
1. Extract the contents to your Home Assistant `custom_components/franklin_wh/` directory.
1. Restart Home Assistant.

______________________________________________________________________

## ⚙️ Configuration

### Easy Setup (Config Flow - Recommended)

1. Go to **Settings → Devices & Services**.

1. Click **+ Add Integration**.

1. Search for **FranklinWH**.

1. Enter your credentials:

   - **Email Address**: Your FranklinWH account email
   - **Password**: Your FranklinWH account password
   - **Use Local API** (optional): Enable for experimental local communication
   - **Local Host** (optional): IP address of your FranklinWH gateway

1. Click **Submit** and your devices will be added automatically!

______________________________________________________________________

## 📊 Available Entities

After setup, all entities will be organized under a single **FranklinWH** device per installation:

### Sensors (some depend on installation accessories and configuration)

| Entity | Description | Unit |
| --- | --- | --- |
| **State of Charge** | Battery state of charge | % |
| **Battery Use** | Battery charging/discharging rate (negative = charging) | kW |
| **Battery Charge** | Total energy charged to battery | kWh |
| **Battery Discharge** | Total energy discharged from battery | kWh |
| **Battery Charge from Grid** | Energy charged to battery from grid (calculated) | kWh |
| **Home Load** | Instantaneous home power consumption | kW |
| **Grid Use** | Net grid power (negative = importing, positive = exporting) | kW |
| **Grid Import** | Total energy imported from grid | kWh |
| **Grid Export** | Total energy exported to grid | kWh |
| **Solar Production** | Instantaneous solar power generation | kW |
| **Solar Energy** | Total solar energy produced | kWh |
| **Home Energy Total** | Total energy consumed by home | kWh |
| **Run Status** | Battery operating status | Standby, Charging, Discharging |
| **Generator Use** | Generator power output (live) | kW |
| **Generator Energy** | Total generator energy produced | kWh |
| **Circuits 1 Use** | Power draw on Switch 1 | kW |
| **Switch 1 Lifetime Use** | Total energy used by Switch 1 | kWh |
| **Circuits 2 Use** | Power draw on Switch 2 | kW |
| **Circuits 2 Lifetime Use** | Total energy used by Switch 2 | kWh |
| **Circuits 3 Use** | Power draw on Switch 3 | kW |
| **Circuits 3 Import** | Total energy drawn from Circuits 3 | kWh |
| **Circuits 3 Export** | Total energy delivered to Circuits 3 | kWh |

### Controls (some depend on installation accessories and configuration)

| Entity | Description |
| --- | --- |
| **Backup Reserve** | Configure minimum Backup Reserve percentage for current Operating Mode |
| **Operating Mode** | Time of Use (TOU), Self-Consumption, Emergency Backup, [VPP](https://www.franklinwh.com/support/overview/virtual-power-plant) |
| **Grid Connection** | Monitor and control grid connection status |
| **Generator** | Import from Generator Module |
| **Circuits 1** | Control smart circuit 1 |
| **Circuits 2** | Control smart circuit 2 |
| **Circuits 3** | Control smart circuit 3 |

______________________________________________________________________

## 🔧 Services (deprecated in favor of Operating Mode and Backup Reserve controls)

The integration provides custom services for advanced control:

### `franklin_wh.set_operation_mode`

Set the operation mode of your FranklinWH system.

**Parameters:**

- `mode`: Operation mode (`self_use`, `backup`, `time_of_use`, `clean_backup`)

**Example:**

```yaml
service: franklin_wh.set_operation_mode
data:
  mode: self_use
```

### `franklin_wh.set_battery_reserve`

Set the minimum battery reserve percentage.

**Parameters:**

- `reserve_percent`: Minimum battery charge to maintain (0-100)

**Example:**

```yaml
service: franklin_wh.set_battery_reserve
data:
  reserve_percent: 20
```

______________________________________________________________________

## 🔋 Energy Dashboard Integration

All energy sensors are compatible with Home Assistant's **Energy Dashboard**:

1. Go to **Settings → Dashboards → Energy**
1. Configure your energy sources:
   - **Solar Production**: Use "Solar Energy" sensor
   - **Battery**: Use "Battery Charge" and "Battery Discharge" sensors
   - **Battery from Grid**: Use "Battery Charge from Grid" sensor (calculated)
   - **Grid**: Use "Grid Import" and "Grid Export" sensors

______________________________________________________________________

## 🐛 Troubleshooting

### No entities appear after setup

1. Check **Settings → System → Logs** for errors containing `franklin_wh`
1. Verify your credentials are correct
1. Ensure FranklinWH cloud services are online

### Authentication errors

1. Try re-authenticating:
   - Go to **Settings → Devices & Services**
   - Find your FranklinWH integration
   - Click **Configure** → **Re-authenticate**
1. Verify your password is correct

### Entities show as "Unavailable"

1. Check your internet connection
1. Verify the FranklinWH cloud service is accessible
1. Check the integration logs for API errors
1. Try reloading the integration

### Gateway Timeout Errors

If you see "Device response timed out":

1. **Verify gateway is online**: Check the FranklinWH mobile app
1. **Check Gateway ID**: Must be exact SN from app (More → Site Address → SN)
1. **FranklinWH cloud status**: Service may be temporarily down
1. **Disable local API**: If enabled, switch back to cloud polling
1. **Wait and retry**: Gateway may be rebooting or updating

### Local API Issues

The local API is **experimental** and may not work:

- Most users should use **cloud polling** (default)
- Local API requires the gateway to support local communication
- If local API times out, disable it and use cloud polling
- Local API support depends on gateway firmware version

### Diagnostics

To get detailed diagnostic information:

1. Go to **Settings → Devices & Services**
1. Find your FranklinWH integration
1. Click the device, then click **Download Diagnostics**
1. Attach the diagnostics file when reporting issues

______________________________________________________________________

## 🔍 Local API Support (Experimental)

This integration includes experimental support for local API communication. Currently, the FranklinWH library primarily uses cloud polling, but local API support is being explored.

**To enable local API (when available):**

1. Enable "Use Local API" during setup
1. Enter your gateway's local IP address
1. The integration will attempt local communication with faster polling (10 seconds vs 60 seconds)

> 📝 **Note**: Local API support depends on the underlying `franklinwh` Python library and may not be fully functional yet. This is an area of active development.

______________________________________________________________________

## 🤝 Contributing

Contributions are welcome! Please fork the repository and open a pull request:

👉 [https://github.com/jkt628/homeassistant-franklinwh](https://github.com/jkt628/homeassistant-franklinwh)

### Development Setup

1. Clone the repository
1. Install development dependencies
1. Use [VS Code with Dev Containers](https://github.com/jkt628/homeassistant-franklinwh-dev) for a consistent environment
1. Test your changes thoroughly before submitting

### Reporting Issues

When reporting issues, please:

1. Download diagnostics from your integration
1. Include Home Assistant and integration versions
1. Provide relevant log entries
1. Describe steps to reproduce

______________________________________________________________________

## 📋 Changelog

### Version 2026.9.0 (current)

- ⬆️ **UPGRADED**: Updated to [@jkt628](https://github.com/jkt628)'s fork of franklinwh library 2026.9.0
- ✨ **NEW**: support multiple installation with accessories
- ✨ **NEW**: Operating Mode monitoring and control
- ✨ **NEW**: Backup Reserve monitoring and control
- ✨ **NEW**: Generator monitoring and control
- 🐛 **FIXED**: Smart Circuits switch controls
- 📝 **DOCS**: Updated README to reflect available features

### Version 1.1.0

- ⬆️ **UPGRADED**: Updated to franklinwh library 1.0.0
- ✨ **NEW**: Full operation mode control (self_use, backup, time_of_use)
- ✨ **NEW**: Battery reserve percentage setting
- ✨ **NEW**: Grid connection switch for monitoring and control
- ✨ **NEW**: Home Energy Total sensor (total home consumption)
- 🐛 **FIXED**: Integration now properly works with franklinwh 1.0.0 API
- ♻️ **IMPROVED**: Updated imports to use properly exported classes
- 📝 **DOCS**: Updated README to reflect available features

### Version 1.0.9

- ⬆️ **UPGRADED**: Updated to franklinwh library 1.0.0
- ✨ **NEW**: Full operation mode control (self_use, backup, time_of_use)
- ✨ **NEW**: Battery reserve percentage setting
- ✨ **NEW**: Grid connection switch for monitoring and control
- ✨ **NEW**: Home Energy Total sensor (total home consumption)
- 🐛 **FIXED**: Integration now properly works with franklinwh 1.0.0 API
- ♻️ **IMPROVED**: Updated imports to use properly exported classes
- 📝 **DOCS**: Updated README to reflect available features

### Version 1.0.7

- 🐛 **CRITICAL FIX**: Removed Grid Connection switch (requires unreleased library version)
- 🐛 **FIXED**: ImportError for AccessoryType and GridStatus classes
- 🐛 **FIXED**: Integration now loads successfully with franklinwh 0.4.1
- ℹ️ **NOTE**: Smart circuit switches (1-3) still work correctly

### Version 1.0.6

- 🐛 **CRITICAL FIX**: Fixed Stats class import from franklinwh.client module
- 🐛 **FIXED**: "cannot import name 'Stats'" ImportError on setup

### Version 1.0.5

- 🐛 **CRITICAL FIX**: Corrected franklinwh package requirement to 0.4.1 (was incorrectly set to 0.5.0 which doesn't exist)
- 🐛 **FIXED**: "Requirements for franklin_wh not found" error on setup

### Version 1.0.4

- ✨ **NEW**: Battery Charge from Grid calculated sensor
- 🐛 **FIXED**: Entities no longer flicker unavailable during temporary failures
- 🐛 **FIXED**: Energy Dashboard compatibility (all sensors in kWh)
- ♻️ **IMPROVED**: Resilient coordinator with 3-failure grace period
- ♻️ **IMPROVED**: Better error logging and failure tracking
- ⚠️ **NOTE**: Grid Connection switch from this version removed in 1.0.7 (library compatibility)

### Version 1.0.0-1.0.3

- ✨ **NEW**: Modern config flow for UI-based setup
- ✨ **NEW**: DataUpdateCoordinator for efficient API polling
- ✨ **NEW**: Device registry integration
- ✨ **NEW**: Diagnostics support
- ✨ **NEW**: Experimental local API support
- ✨ **NEW**: Custom services (placeholders for future features)
- 🐛 **FIXED**: All typos and copy-paste errors in entity IDs
- 🐛 **FIXED**: Consolidated caching logic
- 🐛 **FIXED**: Improved error handling
- ♻️ **REFACTOR**: Complete code modernization
- ♻️ **REFACTOR**: Better entity organization

### Version 0.4.1 (Legacy)

- Initial YAML-based platform configuration by @richo
- Basic sensor and switch support

______________________________________________________________________

## 📄 License

This project is dual-licensed under:

- **MIT License**
- **Apache License 2.0**

You may choose either license when using or contributing to this project.

______________________________________________________________________

## 🙏 Acknowledgments

- **Original Integration**: [@richo](https://github.com/richo) for the initial implementation
- **Python Library**: [`franklinwh-python`](https://github.com/richo/franklinwh-python) by @richo
- **Rewrite**: Joshua Seidel with Anthropic Claude Sonnet 4.5
- **Community**: Thanks to the Home Assistant community
- **Contributors**: Special thanks to all contributors including [@jkt628](https://github.com/jkt628) for Grid Connection switch

______________________________________________________________________

## ⚠️ Disclaimer

This integration is not affiliated with, endorsed by, or supported by FranklinWH. Use at your own risk. The developers are not responsible for any damage to your system or equipment.

______________________________________________________________________

**Enjoy your FranklinWH integration! 🎉**

For support, please open an issue on [GitHub](https://github.com/jkt628/homeassistant-franklinwh/issues).
