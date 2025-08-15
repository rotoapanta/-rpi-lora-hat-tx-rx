#!/usr/bin/env bash
set -e

echo "🔹 Cambiando al directorio raíz del proyecto..."
cd "$(dirname "$0")/.."

# Cargar .env para SERIAL, FREQ, ADDR, etc.
if [[ -f .env ]]; then
  echo "🔹 Cargando configuración desde .env..."
  # shellcheck disable=SC1091
  source .env
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
ADDR="${ADDR:-0}"
POWER="${POWER:-22}"
AIRSPEED="${AIRSPEED:-2400}"
RX_CSV="${RX_CSV:-}"
RX_DEBUG="${RX_DEBUG:-0}"

echo "📡 Ejecutando RECEPTOR:"
echo "    SERIAL=$SERIAL  FREQ=${FREQ}MHz  ADDR=$ADDR"
echo "    POWER=${POWER}dBm  AIRSPEED=$AIRSPEED  CSV=$RX_CSV  DEBUG=$RX_DEBUG"

exec python src/rx_basic.py \
  --serial "$SERIAL" \
  --freq "$FREQ" \
  --addr "$ADDR" \
  --power "$POWER" \
  --airspeed "$AIRSPEED" \
  --csv "$RX_CSV" \
  --debug "$RX_DEBUG"
