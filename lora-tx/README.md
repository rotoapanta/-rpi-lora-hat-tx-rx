# rpi-lora-sensor-tx

LoRa transmitter for SX126x UART modules on Raspberry Pi, with support for:
- USB-to-UART (CP2102, /dev/ttyUSBx)
- Raspberry Pi native UART (/dev/serial0)
- GPIO-based mode control (M0/M1) when the HAT is mounted on the header

Includes a UART driver for the module, a serial/HAT test utility, and two example transmitters: random messages and simulated telemetry (rain + seismic) in compact JSON.

Note: This repository provides the transmitter side. For receiving, use another Raspberry Pi with a compatible HAT configured to the same frequency and air speed.

---

## Features
- USB and native UART transport
  - CP2102 USB-to-UART (/dev/ttyUSBx)
  - Raspberry Pi UART (/dev/serial0)
- Software control of M0/M1 via GPIO (BCM 22 and 27)
- UART driver for E22/SX126x
- Serial test utility for parameter probe (0xC1 0x00 0x09) and bursts
- Transmitters
  - Random payloads (JSON or text)
  - Simulated rain + seismic telemetry (JSON)
- Configuration via .env and/or CLI flags

---

## Hardware (E22 HAT)
Tested with E22 (SX126x) HATs featuring:
- CP2102 (USB-to-UART)
- UART selection jumpers (A/B/C)
- Mode jumpers (M0/M1)
- LEDs: PWR, AUX, TXD/RXD

Typical jumpers (verify on your HAT):
- UART selection (pick exactly one):
  - A closed: USB (CP2102) connected to the module → use /dev/ttyUSBx
  - B closed: Pi UART connected to the module → use /dev/serial0
  - C closed: CP2102 connected to Raspberry Pi console (not for LoRa)
- Mode selection (M0/M1)
  - Open = HIGH; Closed = LOW
  - TX mode: M0 LOW, M1 LOW
  - Config mode: M0 LOW, M1 HIGH
  - WOR: M0 HIGH, M1 LOW
  - Deep sleep: M0 HIGH, M1 HIGH

LEDs (typical):
- RXD/TXD are usually tied to the CP2102. In USB mode (A) they blink with host traffic; in Pi UART mode (B) they may not blink.
- AUX toggles when the module is busy/ready.

---

## Software requirements
- Raspberry Pi with Python 3.11+
- Python packages: python-dotenv, pyserial, lgpio (installed via requirements.txt)
- For GPIO without sudo: on Raspberry Pi OS the PyPI lgpio package generally suffices; some distros may need extra system packages.

Installation (using provided scripts):
```
# 1) Create and prepare the virtualenv
./scripts/create_env.sh

# 2) Activate it when needed
source rpi-lora-env/bin/activate
```
Manual alternative:
```
python3 -m venv rpi-lora-env
source rpi-lora-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration
Define variables in a .env file at the repo root or pass them via CLI flags.

Example .env (do not commit):
```
# Port selection
SERIAL=/dev/serial0        # or /dev/ttyUSB0 if using USB

# Radio
FREQ=915                   # MHz: 410–493 or 850–930 depending on module
ADDR=101                   # Local node address
DEST=65535                 # Destination (broadcast by default)
POWER=22                   # dBm: 10/13/17/22
AIRSPEED=2400              # bps: 1200–62500 (see driver)

# Transmitters
MODE=json                  # for tx_random: json|text
PERIOD=1.0                 # send period (seconds)
STATION=tx01               # station id (tx_sensors)
BUCKET_MM=0.2              # rain bucket size (mm) (tx_sensors)

# Used by scripts/run_tx.sh
TX_TYPE=random             # random|sensors
```

Recommended: keep a .env.example for reference and copy it to .env locally.

---

## Quick start

### Identify the USB serial port
- Connect the HAT over USB (jumper A closed)
- List USB serial devices:
```
ls -l /dev/ttyUSB*
```
- Use the device shown (e.g., /dev/ttyUSB0). If none appears, reconnect or check dmesg and permissions.

### Option A: convenience script
The script reads .env, activates the virtualenv, and launches the selected transmitter.

- USB (A closed) or Pi UART (B closed), depending on your wiring/jumpers A/B.
- Default serial: /dev/serial0 (override in .env if needed).

```
# Run with bash
bash scripts/run_tx.sh                # uses TX_TYPE from .env or defaults to 'random'
bash scripts/run_tx.sh --type sensors
bash scripts/run_tx.sh --type random
```
You can also set TX_TYPE in .env and run without flags:
```
TX_TYPE=sensors bash scripts/run_tx.sh
```

### Option B: run the Python scripts directly
- USB (A closed): use /dev/ttyUSB0 (verify with: ls -l /dev/ttyUSB*)
- Pi UART (B closed): use /dev/serial0 (enable serial HW in raspi-config)

Random (JSON by default):
```
python src/tx_random.py --serial /dev/serial0 --freq 915 --addr 101 \
  --dest 65535 --power 22 --airspeed 2400 --mode json --period 1.0
```

Sensors (simulated rain + seismic):
```
python src/tx_sensors.py --serial /dev/serial0 --freq 915 --addr 101 \
  --dest 65535 --power 22 --airspeed 2400 --period 2.0 \
  --station tx01 --bucket-mm 0.2
```

---

## Transmitters

### 1) Random messages — src/tx_random.py
- Modes: --mode json (default) | --mode text
- Period: --period 1.0 (s)
- Common args: --serial, --freq, --addr, --dest, --power, --airspeed
- Example output (json): {"ts":"2024-01-01T00:00:00+00:00","seq":12,"rand":123456,"val":42.5}

### 2) Sensor telemetry — src/tx_sensors.py
- Includes rain and seismic blocks by default
  - Rain only: --rain
  - Seismic only: --seismic
- Parameters: --station tx01, --bucket-mm 0.2, --period 2.0
- Common args: --serial, --freq, --addr, --dest, --power, --airspeed
- Example payload:
```
{
  "ts":"2024-01-01T00:00:00+00:00",
  "seq":7,
  "station":"tx01",
  "rain":{"intensity_mm_h":0.85,"bucket_mm":0.2,"bucket_tips_total":3,"rain_mm_total":0.6},
  "seismic":{"ax_g":0.001,"ay_g":-0.004,"az_g":0.0005,"pga_g":0.004,"rms_g":0.002}
}
```

Both scripts prepend the JSON payload with an E22-style header (dest_hi, dest_lo, offset, src_hi, src_lo, offset) before sending via UART to the module.

---

## Serial/HAT test utility — scripts/test_hat_serial.py
Typical actions:

- Probe module parameters (USB, no GPIO; set jumpers M0=LOW, M1=HIGH):
```
python scripts/test_hat_serial.py --serial /dev/ttyUSB0 --probe --no-gpio
```

- Send a burst of text (USB, TX mode M0=LOW, M1=LOW):
```
python scripts/test_hat_serial.py --serial /dev/ttyUSB0 --send "HELLO\r\n" --no-gpio --burst 20
```

- Use GPIO control (HAT on header; M0/M1 jumpers open):
```
python scripts/test_hat_serial.py --serial /dev/ttyUSB0 --probe --gpio
```

- Try a different baud rate:
```
python scripts/test_hat_serial.py --serial /dev/ttyUSB0 --probe --no-gpio --baud 19200
```

---

## Raspberry Pi UART (/dev/serial0)
If you use the Pi UART (Jumpers B):
1) Disable serial console/login and enable the hardware serial:
   - raspi-config → Interface Options → Serial
   - Login shell over serial: No
   - Serial port hardware: Yes
2) Reboot. The device will be /dev/serial0.

---

## Troubleshooting
- "setting fail" at startup
  - The module did not acknowledge configuration (common if M0/M1 forced to TX or using USB without GPIO). If it was already configured, it will still transmit.
- No TXD LED blink in Pi UART mode (B)
  - RXD/TXD are typically tied to the CP2102; in B they may not blink. Check AUX LED or use a receiver.
- No response to probe over USB
  - Use A closed and PWR LED on. For probe without GPIO: M0 LOW, M1 HIGH. Try other baud rates (9600/19200/38400/57600/115200) or use --gpio.
- Conflicts with /dev/serial0
  - Disable serial console in raspi-config and reboot.
- Permission denied on /dev/ttyUSBx or /dev/serial0
  - Add your user to dialout: `sudo usermod -aG dialout $USER` and re-login.
- ImportError for pyserial/lgpio
  - Activate the correct virtualenv and run `pip install -r requirements.txt`.

---

## Project structure
- src/sx126x.py: UART driver for E22/SX126x with GPIO control and config retry
- src/tx_random.py: random payload transmitter (JSON/text)
- src/tx_sensors.py: sensor telemetry transmitter (rain + seismic)
- src/RPi/GPIO.py: lightweight RPi.GPIO adapter backed by lgpio (compat)
- scripts/run_tx.sh: launcher that reads .env and activates the venv
- scripts/create_env.sh: creates/activates venv and installs dependencies
- scripts/test_hat_serial.py: utility to test HAT/serial
- requirements.txt: Python dependencies

---

## Regulatory compliance
Operate within the permitted ISM bands and power limits in your region (e.g., 915 MHz or 868 MHz). Use a proper antenna and follow RF safety guidelines.

---

## License
Specify your license (e.g., MIT).

---

## Acknowledgments
- Inspired by demo code for UART E22/SX126x modules
- Uses pyserial and lgpio
