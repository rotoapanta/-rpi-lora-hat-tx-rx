#!/usr/bin/env bash
set -e

echo "🔹 Cambiando al directorio raíz del proyecto..."
cd "$(dirname "$0")/.."

echo "🔹 Creando entorno virtual 'rpi-lora-env'..."
python3 -m venv rpi-lora-env

echo "🔹 Activando entorno virtual..."
source rpi-lora-env/bin/activate

echo "🔹 Actualizando pip..."
pip install --upgrade pip

echo "🔹 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo "🔹 Entorno virtual 'rpi-lora-env' listo para usar."
echo "🔹 Para activarlo en el futuro: source rpi-lora-env/bin/activate"
echo "🔹 Para desactivarlo: deactivate"