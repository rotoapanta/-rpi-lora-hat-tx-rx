# rpi-lora-hat-tx-rx

Proyecto con dos componentes separados para trabajar con HATs LoRa SX126x en Raspberry Pi:
- lora-tx: transmisor (mensajes aleatorios o telemetría simulada de sensores)
- lora-rx: receptor (con registro opcional a CSV)

Cada componente mantiene su propio entorno virtual y su configuración .env.

## Requisitos
- Raspberry Pi con Python 3.11+
- HAT/placa LoRa basada en SX126x (E22 u otro compatible)
- Antena adecuada y permisos en tu región para operar en la frecuencia elegida

## Preparación de entornos
Se recomiendan entornos virtuales independientes por cada carpeta (TX y RX).

### RX
Dentro de lora-rx/ hay un script de conveniencia:

```bash
bash lora-rx/scripts/create_env.sh
```

Este script crea y prepara el entorno virtual rpi-lora-env e instala dependencias.

### TX
Para TX puedes crear el entorno manualmente (dentro de lora-tx/):

```bash
cd lora-tx
python3 -m venv rpi-lora-env
source rpi-lora-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuración (.env)
Ambos módulos leen variables desde un archivo .env en su raíz correspondiente.

### RX (.env)
Hay un archivo de ejemplo listo para copiar:

```bash
cp lora-rx/.env.example lora-rx/.env
```

Variables principales en lora-rx/.env:
- SERIAL: /dev/ttyUSB0 (USB, jumper A) o /dev/serial0 (GPIO, jumper B)
- FREQ: frecuencia en MHz (por ejemplo, 915 o 868, según tu región/módulo)
- ADDR: dirección propia del RX (p. ej., 102 si el TX usa 101)
- POWER: potencia del radio (parámetro del driver)
- AIRSPEED: velocidad de aire en bps (debe coincidir con TX)
- RX_CSV: ruta del CSV para registrar tramas recibidas (vacío para desactivar)
- RX_DEBUG: 0/1 para depuración de datos crudos

### TX (.env)
También hay un ejemplo en lora-tx/.env.example (si no existe .env, cópialo):

```bash
cp lora-tx/.env.example lora-tx/.env
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

### Receptor (RX)

```bash
bash lora-rx/scripts/run_rx.sh
```

El script activa el venv, carga .env, muestra la configuración efectiva y lanza src/rx_basic.py con flags:
--serial, --freq, --addr, --power, --airspeed, --csv, --debug.

### Transmisor (TX)

```bash
bash lora-tx/scripts/run_tx.sh
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
- lora-tx/
  - src/: tx_random.py, tx_sensors.py, sx126x.py
  - scripts/: run_tx.sh
  - requirements.txt, .env(.example)
- lora-rx/
  - src/: rx_basic.py, sx126x.py
  - scripts/: run_rx.sh, create_env.sh
  - requirements.txt, .env(.example)
- .gitignore (global del proyecto)

## Cumplimiento normativo
Opera dentro de las bandas ISM y límites de potencia permitidos en tu región (p. ej., 915 MHz o 868 MHz). Usa una antena adecuada y sigue las guías de seguridad RF.

## Licencia
Ver LICENSE.
