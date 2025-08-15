#!/usr/bin/env python3
import argparse, time, sys, os, glob

# Asegura que el adaptador GPIO local (src/RPi/GPIO.py) esté disponible
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None

try:
    import serial
except Exception as e:
    print("Falta pyserial: pip install pyserial", file=sys.stderr)
    raise

# Pines BCM del HAT según el driver
M0 = 22
M1 = 27

def detect_serial_default() -> str:
    # Preferir USB si está conectado
    usb = sorted(glob.glob('/dev/ttyUSB*'))
    if usb:
        return usb[0]
    # Si no hay USB, usar la UART de la Pi
    return '/dev/serial0'

def set_mode(config_mode: bool, use_gpio: bool):
    if not use_gpio:
        return
    if GPIO is None:
        print("GPIO no disponible en este entorno (usa --no-gpio si estás en USB/CP2102 o fija M0/M1 por jumpers)")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(M0, GPIO.OUT)
    GPIO.setup(M1, GPIO.OUT)
    if config_mode:
        # M0=LOW, M1=HIGH => modo configuración
        GPIO.output(M0, GPIO.LOW)
        GPIO.output(M1, GPIO.HIGH)
    else:
        # M0=LOW, M1=LOW => modo transmisión
        GPIO.output(M0, GPIO.LOW)
        GPIO.output(M1, GPIO.LOW)
    time.sleep(0.5)


def probe_settings(ser: serial.Serial, timeout=1.5) -> bytes:
    # Comando para leer parámetros: 0xC1 0x00 0x09
    ser.reset_input_buffer()
    ser.write(bytes([0xC1, 0x00, 0x09]))
    ser.flush()
    end = time.time() + timeout
    buf = bytearray()
    while time.time() < end:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting)
        if len(buf) >= 3 and buf[0] == 0xC1 and buf[2] == 0x09:
            break
        time.sleep(0.05)
    return bytes(buf)


def main():
    ap = argparse.ArgumentParser(description="Prueba puerto serial del HAT SX126x")
    ap.add_argument('--serial', default=None, help='Dispositivo serie (/dev/serial0 o /dev/ttyUSB0). Si se omite, se autodetecta.')
    ap.add_argument('--baud', type=int, default=9600)
    ap.add_argument('--probe', action='store_true', help='Intentar leer parámetros del módulo (modo configuración)')
    ap.add_argument('--send', default='', help="Enviar texto crudo para ver actividad en UART (e.g. 'HELLO\\r\\n')")
    ap.add_argument('--gpio', dest='use_gpio', action='store_true', help='Controlar M0/M1 por GPIO (requiere HAT sobre el header y M0/M1 sin jumpers)')
    ap.add_argument('--no-gpio', dest='use_gpio', action='store_false', help='No controlar M0/M1 por GPIO (usar cuando fijas el modo con jumpers o vas por USB)')
    ap.set_defaults(use_gpio=None)
    # Compatibilidad con la versión previa
    ap.add_argument('--skip-gpio', action='store_true', help='Alias de --no-gpio')
    ap.add_argument('--burst', type=int, default=1, help='Repetir el envío N veces (para observar LEDs)')
    args = ap.parse_args()

    # Autodetectar puerto si no se especifica
    serial_dev = args.serial or detect_serial_default()

    # Resolver uso de GPIO automáticamente si no se especificó
    if args.use_gpio is None:
        # Si vamos por USB, por defecto NO usar GPIO; si vamos por /dev/serial0, usar GPIO si está disponible
        args.use_gpio = (not serial_dev.startswith('/dev/ttyUSB')) and (GPIO is not None)
    # Respetar alias --skip-gpio
    if args.skip_gpio:
        args.use_gpio = False

    # Determinar modo deseado para M0/M1
    config_mode = bool(args.probe)

    # Mensajes guía sobre jumpers según contexto
    if not args.use_gpio:
        if serial_dev.startswith('/dev/ttyUSB'):
            # USB/CP2102
            if config_mode:
                print("Nota: con USB y sin GPIO, fija jumpers: A cerrado; M0 cerrado, M1 abierto (modo configuración)")
            else:
                print("Nota: con USB y sin GPIO, fija jumpers: A cerrado; M0 cerrado, M1 cerrado (modo transmisión)")
        else:
            print("Advertencia: sin GPIO y usando /dev/serial0, asegúrate de fijar M0/M1 por jumpers (LOW/LOW para transmitir, LOW/HIGH para configurar)")

    # Si vamos a hacer probe, entrar en modo config; si sólo enviar texto, modo transmisión
    set_mode(config_mode=config_mode, use_gpio=args.use_gpio)

    print(f"Abriendo {serial_dev} @ {args.baud} bps…")
    try:
        ser = serial.Serial(serial_dev, args.baud, timeout=0.2)
    except Exception as e:
        print(f"Error abriendo {serial_dev}: {e}")
        sys.exit(1)

    time.sleep(0.1)

    did = False
    if args.probe:
        did = True
        print("Probing parámetros (0xC1 0x00 0x09)…")
        resp = probe_settings(ser)
        if resp.startswith(b'\xC1') and len(resp) >= 3 and resp[2] == 0x09:
            print(f"OK: respuesta {resp.hex()}")
        else:
            print(f"Sin respuesta válida (recibido {resp.hex() if resp else 'nada'})")
        # Volver a modo transmisión si controlamos GPIO
        set_mode(config_mode=False, use_gpio=args.use_gpio)

    if args.send:
        did = True
        data = args.send.encode()
        print(f"Enviando {len(data)} bytes x {args.burst}…")
        for i in range(max(1, args.burst)):
            ser.write(data)
            ser.flush()
            time.sleep(0.05)
        print("Enviado. Observa LEDs/analizador/receptor.")

    if not did:
        print("Nada que hacer: use --probe o --send 'TEXTO'")

    ser.close()

if __name__ == '__main__':
    main()
