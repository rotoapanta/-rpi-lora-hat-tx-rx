#!/usr/bin/env bash
set -e

echo "🔹 Cambiando al directorio raíz del proyecto..."
cd "$(dirname "$0")/.."

# Cargar .env antes para poder leer TX_TYPE, STATION, BUCKET_MM, etc.
if [[ -f .env ]]; then
  echo "🔹 Cargando configuración desde .env..."
  # shellcheck disable=SC1091
  source .env
fi

# Parseo simple de --type
TX_TYPE_CLI=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TX_TYPE_CLI="$2"; shift 2;;
    --type=*)
      TX_TYPE_CLI="${1#*=}"; shift 1;;
    *)
      echo "⚠️  Argumento no reconocido para run_tx.sh: $1"; shift 1;;
  esac
done

# Decide tipo (CLI > env > default)
TX_TYPE="${TX_TYPE_CLI:-${TX_TYPE:-random}}"
TX_TYPE_LOWER="$(echo "$TX_TYPE" | tr '[:upper:]' '[:lower:]')"
if [[ "$TX_TYPE_LOWER" != "random" && "$TX_TYPE_LOWER" != "sensors" ]]; then
  echo "❌ TX_TYPE inválido: '$TX_TYPE'. Usa 'random' o 'sensors'."
  exit 1
fi

# Activa el venv solo si no está ya activo
if [[ "$VIRTUAL_ENV" != "$(pwd)/rpi-lora-env" ]]; then
  echo "🔹 Activando entorno virtual 'rpi-lora-env'..."
  # shellcheck disable=SC1091
  source rpi-lora-env/bin/activate
else
  echo "ℹ️  Entorno virtual ya activo: $VIRTUAL_ENV"
fi

# Defaults por si no existen en .env
SERIAL="${SERIAL:-/dev/serial0}"
FREQ="${FREQ:-915}"
ADDR="${ADDR:-101}"
DEST="${DEST:-65535}"
POWER="${POWER:-22}"
AIRSPEED="${AIRSPEED:-2400}"
PERIOD="${PERIOD:-1.0}"
MODE="${MODE:-json}"
STATION="${STATION:-tx01}"
BUCKET_MM="${BUCKET_MM:-0.2}"

if [[ "$TX_TYPE_LOWER" == "random" ]]; then
  echo "🚀 Ejecutando TRANSMISOR (random):"
  echo "    SERIAL=$SERIAL  FREQ=${FREQ}MHz  ADDR=$ADDR  DEST=$DEST"
  echo "    POWER=${POWER}dBm  AIRSPEED=$AIRSPEED  MODE=$MODE  PERIOD=${PERIOD}s"

  exec python src/tx_random.py \
    --serial "$SERIAL" \
    --freq "$FREQ" \
    --addr "$ADDR" \
    --dest "$DEST" \
    --power "$POWER" \
    --airspeed "$AIRSPEED" \
    --mode "$MODE" \
    --period "$PERIOD"

else
  echo "🚀 Ejecutando TRANSMISOR (sensors):"
  echo "    SERIAL=$SERIAL  FREQ=${FREQ}MHz  ADDR=$ADDR  DEST=$DEST"
  echo "    POWER=${POWER}dBm  AIRSPEED=$AIRSPEED  PERIOD=${PERIOD}s"
  echo "    STATION=$STATION  BUCKET_MM=$BUCKET_MM  (sin --mode)"

  exec python src/tx_sensors.py \
    --serial "$SERIAL" \
    --freq "$FREQ" \
    --addr "$ADDR" \
    --dest "$DEST" \
    --power "$POWER" \
    --airspeed "$AIRSPEED" \
    --period "$PERIOD" \
    --station "$STATION" \
    --bucket-mm "$BUCKET_MM"
fi
