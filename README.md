<<<<<<< HEAD
# SteamOS LED → WLED

Mirrors the Steam Deck's LED bar to a [WLED](https://github.com/Aircoookie/WLED) controller via UDP DRGB, USB serial, or both. USB serial mode sends WLED-compatible Adalight frames directly to WLED running on the connected ESP32-S3. The 17 source LEDs are remapped to the configured strip length (1–256) with weighted averaging; the output is treated as one linear strip, not a matrix.

No custom MCU firmware is needed. The ESP32-S3 runs WLED, which receives the LED frames over USB serial and drives its configured LED output.

**[简体中文](README.zh-CN.md) | [Leia em Português (PT-BR)](README.pt-br.md)**
=======
# SteamOS LED → WLED Bridge

Mirrors the Steam Deck's LED bar to a [WLED](https://github.com/Aircoookie/WLED) controller via UDP realtime protocol (DRGB).

No custom firmware needed — just a stock WLED device on your network.

**[Leia em Português (PT-BR)](README.pt-br.md)**
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

## How it works

1. Reads 100-byte LED snapshots from `/dev/valve-leds-shim` (kernel module)
2. Remaps 17 source LEDs to your strip length
3. Renders Steam Deck effects server-side (rainbow, breath, patrol, factory, demo)
4. Applies optional overlays (temperature, notifications, audio VU)
<<<<<<< HEAD
5. Sends pixel data via **UDP DRGB** to WLED and/or **Adalight** over USB serial
=======
5. Sends pixel data via **UDP DRGB** (port 21324) to WLED — same protocol HyperHDR uses
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
6. Plays boot/shutdown/suspend/resume animations

## Requirements

- **Steam Deck** (SteamOS) or Linux PC running Steam in Game Mode
<<<<<<< HEAD
- **WLED device** on the same network when using WLED output
- **WLED-capable controller** when using USB serial output; a Waveshare ESP32-S3-Matrix is supported when its WLED build exposes USB serial
- **Python 3** (the installer adds it on supported distros if missing; the bridge uses only the standard library)

### Setting up WLED

For UDP output, set up a WLED controller on your network before installing this bridge. USB serial-only output does not require Wi-Fi or a WLED IP address. Quick steps for network output:
=======
- **WLED device** on the same network (ESP8266, ESP32, etc.)
- **Python 3** (no extra packages needed — uses only stdlib)

### Setting up WLED (prerequisite)

You need a WLED controller on your network before installing this bridge. Quick steps:
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

1. **Flash WLED** to an ESP8266 or ESP32 board:
   - Download the latest release from [WLED releases](https://github.com/Aircoookie/WLED/releases)
   - Use the [WLED web installer](https://install.wled.me/) (Chrome/Edge) for easiest setup
2. **Connect to WiFi**: After flashing, connect to the `WLED-AP` hotspot and configure your WiFi credentials
3. **Configure LED strip**: In WLED settings → LED Preferences, set the correct LED count and type (WS2812B, SK6812, etc.)
4. **Note the IP address**: WLED shows its IP on the main page. The installer can also auto-discover it
5. **Enable UDP sync**: In WLED settings → Sync Interfaces, ensure the UDP port is **21324** (default)

For detailed instructions, see the [WLED documentation](https://kno.wled.ge/).

## Installation

```bash
git clone https://github.com/rpf16rj/steamos-led-wled.git
cd steamos-led-wled
sudo ./install.sh
```

The installer will:
<<<<<<< HEAD

1. Ask whether to use WLED, USB, or both
2. Auto-discover WLED devices (mDNS / subnet scan) when WLED output is selected
3. Ask for the USB serial device when USB output is selected
4. Ask for logical LED count and overlay preferences
5. Install required system packages, including Python 3 if it is missing
6. Build and install the `leds-valve-shim` kernel module
7. Install the bridge service and generate `/etc/steamos-led-wled.conf`
8. Enable and start the systemd service

### WLED on the ESP32-S3-Matrix

Flash a WLED build that supports the ESP32-S3 board and exposes its USB serial interface. In WLED LED Preferences, configure the onboard LED data pin (GPIO 14 on the Waveshare ESP32-S3-Matrix), LED type, and LED count to match `num_leds`. WLED's serial interface supports Adalight; configure its serial baud rate in Sync settings to match `usb_serial_baud` (default `115200`). USB-only output does not require Wi-Fi or a WLED IP address.

The host device is usually `/dev/ttyACM0`. Ensure the service user can access it (commonly via the `dialout` or `uucp` group). See the [WLED serial documentation](https://kno.wled.ge/interfaces/serial/) and the [Waveshare board reference](https://www.waveshare.com/wiki/ESP32-S3-Matrix).
=======
1. Try to **auto-discover** WLED devices on your network (mDNS / subnet scan)
2. Fall back to asking for the IP address manually
3. Ask for LED count and overlay preferences
4. Build and install the `leds-valve-shim` kernel module
5. Install the bridge service and generate `/etc/steamos-led-wled.conf`
6. Enable and start the systemd service
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

## Decky Loader Plugin

Control overlays directly from Game Mode using the **Toolkit SteamOS Control** Decky plugin:

- Repository: [toolkit-steamos-control-decky](https://github.com/rpf16rj/toolkit-steamos-control-decky)
- Toggle temperature, audio VU, and notification overlays without leaving Game Mode

## Configuration

Edit `/etc/steamos-led-wled.conf`:

```ini
[steamos-led-wled]
<<<<<<< HEAD
# wled (UDP), usb (WLED Adalight over USB serial), or both
output_mode = wled

=======
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
# WLED device IP address
wled_host = 192.168.1.100

# WLED UDP realtime port (default: 21324)
wled_port = 21324

<<<<<<< HEAD
# Number of logical LEDs sent to the output (1-256)
num_leds = 8

# WLED USB serial device and baud rate
usb_serial_device = /dev/ttyACM0
usb_serial_baud = 115200

# USB serial protocol: adalight (default) or json (WLED JSON over Serial)
usb_serial_protocol = adalight

=======
# Number of LEDs on your strip (1-17)
num_leds = 8

>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
# Path to the valve-leds-shim device
device = /dev/valve-leds-shim

# Overlay features (true/false)
temp_overlay = true
notify_overlay = true
audio_overlay = true
```

<<<<<<< HEAD
The source contains 17 LEDs. `num_leds` can be set from 1 to 256: smaller outputs use weighted averaging to combine source LEDs, while larger outputs distribute the source LEDs across the strip using weighted averages at source boundaries. Configure the WLED strip to match `num_leds`. USB-only output does not use `wled_host`; set `output_mode = usb`. Set `output_mode = both` to mirror each remapped frame to WLED over UDP and USB serial.

Choose the USB serial protocol during installation or set `usb_serial_protocol` manually: `adalight` (default, binary Adalight frames) or `json` (newline-delimited WLED JSON API commands over Serial). This setting is used only when `output_mode` is `usb` or `both`.

=======
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
After editing, restart the service:

```bash
sudo systemctl restart steamos-led-wled
```

## Features

### LED Effects (server-side rendering)

<<<<<<< HEAD
All Steam Deck LED effects are rendered by the bridge and sent to the configured output(s):

| Effect            | Description                      |
| ----------------- | -------------------------------- |
| **Manual**  | Static color set by Game Mode    |
| **Rainbow** | Cycling hues across all LEDs     |
| **Breath**  | Pulsing brightness               |
| **Patrol**  | Ping-pong bouncing light         |
| **Factory** | Alternating complementary colors |
| **Demo**    | Cycles through all effects       |

### Overlay features

| Overlay                 | Description                                                |
| ----------------------- | ---------------------------------------------------------- |
| **Temperature**   | Colors the bar yellow→red based on CPU/GPU temp (> 65°C) |
| **Notifications** | Flashes gold for achievements, blue for messages           |
| **Audio VU**      | VU meter driven by system audio (PipeWire/PulseAudio)      |
=======
All Steam Deck LED effects are rendered by the bridge and sent to WLED:

| Effect | Description |
|--------|-------------|
| **Manual** | Static color set by Game Mode |
| **Rainbow** | Cycling hues across all LEDs |
| **Breath** | Pulsing brightness |
| **Patrol** | Ping-pong bouncing light |
| **Factory** | Alternating complementary colors |
| **Demo** | Cycles through all effects |

### Overlay features

| Overlay | Description |
|---------|-------------|
| **Temperature** | Colors the bar yellow→red based on CPU/GPU temp (> 65°C) |
| **Notifications** | Flashes gold for achievements, blue for messages |
| **Audio VU** | VU meter driven by system audio (PipeWire/PulseAudio) |
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

Priority: Notification > Audio+Temperature > Game Mode

### Animations

<<<<<<< HEAD
| Event              | Animation                                  |
| ------------------ | ------------------------------------------ |
| **Boot**     | Center-out sweep in Steam blue, then pulse |
| **Shutdown** | Edge-to-center fade out                    |
| **Suspend**  | Slow fade to black                         |
| **Resume**   | Quick center-out sweep                     |
=======
| Event | Animation |
|-------|-----------|
| **Boot** | Center-out sweep in Steam blue, then pulse |
| **Shutdown** | Edge-to-center fade out |
| **Suspend** | Slow fade to black |
| **Resume** | Quick center-out sweep |
>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6

## Commands

```bash
# Check status
sudo systemctl status steamos-led-wled

# View logs
sudo journalctl -u steamos-led-wled -f

# Restart
sudo systemctl restart steamos-led-wled

# Stop
sudo systemctl stop steamos-led-wled
```

## Uninstall

```bash
sudo ./uninstall.sh
```

## UDP Protocol

Uses WLED's **DRGB** realtime protocol on port 21324:

<<<<<<< HEAD
| Byte   | Value    | Description           |
| ------ | -------- | --------------------- |
| 0      | `0x02` | Protocol: DRGB        |
| 1      | `0x02` | Timeout: 2 seconds    |
| 2+n×3 | R        | Red value for LED n   |
| 3+n×3 | G        | Green value for LED n |
| 4+n×3 | B        | Blue value for LED n  |

This is the same protocol used by HyperHDR, Hyperion, and other ambilight solutions.

## USB Serial Protocol

USB output sends complete RGB frames using WLED's Adalight serial protocol:

| Field       | Size       | Description                                                  |
| ----------- | ---------- | ------------------------------------------------------------ |
| Header      | 3 bytes    | ASCII `Ada`                                                  |
| Pixel count | 2 bytes    | Big-endian count minus one                                   |
| Checksum    | 1 byte     | High count byte XOR low count byte XOR `0x55`                |
| Payload     | 3 × count  | RGB bytes in physical LED-chain order (up to 256 from host)  |

This is the serial protocol documented by WLED for real-time LED data. The previous `SLW1` custom MCU protocol is no longer sent; flash WLED on the ESP32-S3 instead of building the separate MCU firmware.

=======
| Byte | Value | Description |
|------|-------|-------------|
| 0 | `0x02` | Protocol: DRGB |
| 1 | `0x02` | Timeout: 2 seconds |
| 2+n×3 | R | Red value for LED n |
| 3+n×3 | G | Green value for LED n |
| 4+n×3 | B | Blue value for LED n |

This is the same protocol used by HyperHDR, Hyperion, and other ambilight solutions.

>>>>>>> 3e414fbe9493877576bd8ec237095d71b28574b6
## License

MIT
