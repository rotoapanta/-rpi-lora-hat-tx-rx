[![Python](https://img.shields.io/badge/Python-3.11-brightgreen)](https://www.python.org/) 
![GitHub issues](https://img.shields.io/github/issues/rotoapanta/raspberry-api) 
![GitHub repo size](https://img.shields.io/github/repo-size/rotoapanta/raspberry-api) 
![GitHub last commit](https://img.shields.io/github/last-commit/rotoapanta/raspberry-api)
[![Discord Invite](https://img.shields.io/badge/discord-join%20now-green)](https://discord.gg/bf6rWDbJ) 
[![Docker](https://img.shields.io/badge/Docker-No-brightgreen)](https://www.docker.com/) 
[![GitHub](https://img.shields.io/badge/GitHub-Project-brightgreen)](https://github.com/rotoapanta/raspberry-api) 
[![Linux](https://img.shields.io/badge/Linux-Supported-brightgreen)](https://www.linux.org/) 
[![Author](https://img.shields.io/badge/Roberto%20-Toapanta-brightgreen)](https://www.linkedin.com/in/roberto-carlos-toapanta-g/) 
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](#change-log) 
![GitHub forks](https://img.shields.io/github/forks/rotoapanta/raspberry-api?style=social) 
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# <p align="center">RPI LoRa HAT Tx and Rx</p>

Project with two separate components to work with LoRa SX126x HATs on Raspberry Pi:
- lora-tx: transmitter (random messages or simulated sensor telemetry)
- lora-rx: receiver (optional CSV logging)

Each component maintains its own virtual environment and .env configuration.

## Requirements
- Raspberry Pi 5 with Python 3.11+
- LoRa HAT/board based on SX126x
- Proper antenna and regulatory permission to operate at your selected frequency

## Clone the repository

```bash
$ git clone git@github.com:rotoapanta/rpi-lora-hat-tx-rx.git
$ cd rpi-lora-hat-tx-rx
```

## Project structure

```
rpi-lora-hat-tx-rx/
├── .git/                     # root repo
├── .gitignore                # project-wide ignores
├── LICENSE
├── README.md
├── lora-tx/                  # transmitter
│   ├── .env                  # TX configuration
│   ├── .env.example
│   ├── requirements.txt
│   ├── rpi-lora-env/         # virtualenv (ignored by git)
│   ├── scripts/
│   │   ├── create_env.sh
│   │   ├── run_tx.sh
│   │   └── test_hat_serial.py
│   └── src/
│       ├── RPi/
│       ├── sx126x.py
│       ├── tx_random.py
│       └── tx_sensors.py
└── lora-rx/                  # receiver
    ├── .env                  # RX configuration
    ├── .env.example
    ├── requirements.txt
    ├── rx_log.csv            # sample/generated CSV
    ├── scripts/
    │   ├── create_env.sh
    │   ├── run_rx.sh
    │   └── test_hat_serial.py
    └── src/
        ├── RPi/
        ├── rx_basic.py
        └── sx126x.py
```

## Environment setup
Separate virtual environments are recommended for TX and RX.

### LoRa Rx
Inside lora-rx/ there is a convenience script:

```bash
$ ./scripts/create_env.sh
```

This script creates the rpi-lora-env virtual environment and installs dependencies.

### LoRa Tx
Inside lora-tx/ there is a convenience script:

```bash
$ ./scripts/create_env.sh
```

This script creates the rpi-lora-env virtual environment and installs dependencies.

## Configuration (.env)
Both modules read variables from a .env file at their respective roots.

### LoRa Rx (.env)
An example file is available:

```bash
$ cp lora-rx/.env.example lora-rx/.env
```

Key variables in lora-rx/.env:
- SERIAL: /dev/ttyUSB0 (USB, jumper A) or /dev/serial0 (GPIO, jumper B)
- FREQ: frequency in MHz (e.g., 915 or 868, depending on region/module)
- ADDR: RX address (e.g., 102 if TX uses 101)
- POWER: radio power (driver parameter)
- AIRSPEED: air speed in bps (must match TX)
- RX_CSV: path to CSV to log received frames (empty to disable)
- RX_DEBUG: 0/1 to print raw serial data

### LoRa Tx (.env)
An example file is available under lora-tx/.env.example (copy it if missing):

```bash
$ cp lora-tx/.env.example lora-tx/.env
```

Key variables in lora-tx/.env:
- SERIAL: /dev/ttyUSB0 (USB, jumper A) or /dev/serial0 (GPIO, jumper B)
- FREQ: frequency in MHz (must match RX)
- ADDR: TX address (e.g., 101)
- DEST: 65535 (broadcast) or the target RX ADDR (e.g., 102)
- POWER: transmit power in dBm
- AIRSPEED: air speed in bps (must match RX)
- PERIOD: send period in seconds
- TX_TYPE: random | sensors (selects which script to run)
- MODE: json | text (only for TX_TYPE=random)
- STATION, BUCKET_MM: parameters for sensors mode

Compatibility notes:
- FREQ and AIRSPEED must match EXACTLY between TX and RX.
- Using DEST=65535 (broadcast) allows any RX with matching FREQ/AIRSPEED to receive.

## Run

### LoRa Rx

```bash
$ ./lora-rx/scripts/run_rx.sh
```

The script activates the venv, loads .env, prints the effective configuration and starts src/rx_basic.py with flags:
--serial, --freq, --addr, --power, --airspeed, --csv, --debug.

### LoRa Tx

```bash
$ ./lora-tx/scripts/run_tx.sh
```

The script activates the venv, loads .env and selects the transmitter based on TX_TYPE (random or sensors), launching:
- src/tx_random.py with --serial --freq --addr --dest --power --airspeed --mode --period
- src/tx_sensors.py with --serial --freq --addr --dest --power --airspeed --period --station --bucket-mm

You can override variables inline, for example:

```bash
TX_TYPE=sensors bash lora-tx/scripts/run_tx.sh
RX_DEBUG=1 bash lora-rx/scripts/run_rx.sh
```

## Regulatory compliance
Operate within the permitted ISM bands and power limits in your region (e.g., 915 MHz or 868 MHz). Use an appropriate antenna and follow RF safety guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- [@rotoapanta](https://github.com/rotoapanta)

## More Info

- [Waveshare SX1262 868M LoRa HAT (product page)](https://www.waveshare.com/sx1262-868m-lora-hat.htm?sku=16807)
- [Waveshare SX1262 868M LoRa HAT (wiki)](https://www.waveshare.com/wiki/SX1262_868M_LoRa_HAT)

## Links

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/roberto-carlos-toapanta-g/)
[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/rotoapanta)
