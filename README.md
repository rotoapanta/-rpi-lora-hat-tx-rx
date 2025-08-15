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

# <p align="center">rpi-lora-hat-tx-rx</p>

Proyecto con dos componentes separados para trabajar con HATs LoRa SX126x en Raspberry Pi:
- lora-tx: transmisor (mensajes aleatorios o telemetría simulada de sensores)
- lora-rx: receptor (con registro opcional a CSV)

Cada componente mantiene su propio entorno virtual y su configuración .env.

## Requisitos
- Raspberry Pi con Python 3.11+
- HAT/placa LoRa basada en SX126x
- Antena adecuada y permisos en tu región para operar en la frecuencia elegida

## Preparación de entornos
Se recomiendan entornos virtuales independientes por cada carpeta (Tx y Rx).

### LoRa Rx
Dentro de lora-rx/ hay un script de conveniencia:

```bash
$ ./create_env.sh
```

Este script crea y prepara el entorno virtual rpi-lora-env e instala dependencias.

### LoRa Tx
Dentro de lora-rx/ hay un script de conveniencia:

```bash
$ ./create_env.sh
```

Este script crea y prepara el entorno virtual rpi-lora-env e instala dependencias.

## Configuración (.env)
Ambos módulos leen variables desde un archivo .env en su raíz correspondiente.

### LoRa Rx (.env)
Hay un archivo de ejemplo listo para copiar:

```bash
$ cp lora-rx/.env.example lora-rx/.env
```

Variables principales en lora-rx/.env:
- SERIAL: /dev/ttyUSB0 (USB, jumper A) o /dev/serial0 (GPIO, jumper B)
- FREQ: frecuencia en MHz (por ejemplo, 915 o 868, según tu región/módulo)
- ADDR: dirección propia del RX (p. ej., 102 si el TX usa 101)
- POWER: potencia del radio (parámetro del driver)
- AIRSPEED: velocidad de aire en bps (debe coincidir con TX)
- RX_CSV: ruta del CSV para registrar tramas recibidas (vacío para desactivar)
- RX_DEBUG: 0/1 para depuración de datos crudos

### LoRa Tx (.env)
También hay un ejemplo en lora-tx/.env.example (si no existe .env, cópialo):

```bash
$ cp lora-tx/.env.example lora-tx/.env
```

Variables principales en lora-tx/.env:
- SERIAL: /dev/ttyUSB0 (USB, jumper A) o /dev/serial0 (GPIO, jumper B)
- FREQ: frecuencia en MHz (debe coincidir con RX)
- ADDR: dirección propia del TX (p. ej., 101)
- DEST: 65535 (broadcast) o la ADDR del RX destino (p. ej., 102)
- POWER: potencia de transmisión en dBm
- AIRSPEED: velocidad de aire en bps (debe coincidir con RX)
- PERIOD: periodo de envío en segundos
- TX_TYPE: random | sensors (selecciona script a ejecutar)
- MODE: json | text (solo para TX_TYPE=random)
- STATION, BUCKET_MM: parámetros del modo sensors

Notas de compatibilidad:
- FREQ y AIRSPEED deben coincidir EXACTAMENTE entre TX y RX.
- Si usas DEST=65535 (broadcast), cualquier RX que coincida en FREQ/AIRSPEED recibirá.

## Ejecución

### LoRa Rx

```bash
$ ./lora-rx/scripts/run_rx.sh
```

El script activa el venv, carga .env, muestra la configuración efectiva y lanza src/rx_basic.py con flags:
--serial, --freq, --addr, --power, --airspeed, --csv, --debug.

### LoRa Tx

```bash
$ ./lora-tx/scripts/run_tx.sh
```

El script activa el venv, carga .env y elige el transmisor según TX_TYPE (random o sensors), lanzando:
- src/tx_random.py con --serial --freq --addr --dest --power --airspeed --mode --period
- src/tx_sensors.py con --serial --freq --addr --dest --power --airspeed --period --station --bucket-mm

Puedes sobreescribir variables al vuelo, por ejemplo:

```bash
TX_TYPE=sensors bash lora-tx/scripts/run_tx.sh
RX_DEBUG=1 bash lora-rx/scripts/run_rx.sh
```

## Estructura del proyecto

```
rpi-lora-hat-tx-rx/
├── .git/                     # repo raíz
├── .gitignore                # ignore global del proyecto
├── LICENSE
├── README.md
├── lora-tx/                  # transmisor
│   ├── .env                  # configuración TX
│   ├── .env.example
│   ├── requirements.txt
│   ├── rpi-lora-env/         # entorno virtual (ignorado por git)
│   ├── scripts/
│   │   ├── create_env.sh
│   │   ├── run_tx.sh
│   │   └── test_hat_serial.py
│   └── src/
│       ├── RPi/
│       ├── __pycache__/
│       ├── sx126x.py
│       ├── tx_random.py
│       └── tx_sensors.py
└── lora-rx/                  # receptor
    ├── .env                  # configuración RX
    ├── .env.example
    ├── requirements.txt
    ├── rx_log.csv            # CSV de ejemplo/generado por RX
    ├── scripts/
    │   ├── create_env.sh
    │   ├── run_rx.sh
    │   └── test_hat_serial.py
    └── src/
        ├── RPi/
        ├── __pycache__/
        ├── rx_basic.py
        └── sx126x.py
```

Notas:
- Los directorios __pycache__/ y rpi-lora-env/ están ignorados por .gitignore.
- lora-tx originalmente contenía un .git propio; decide si integrarlo en el repo raíz o mantenerlo aparte.

## Cumplimiento normativo
Opera dentro de las bandas ISM y límites de potencia permitidos en tu región (p. ej., 915 MHz o 868 MHz). Usa una antena adecuada y sigue las guías de seguridad RF.

## Licencia
Ver LICENSE.
