#!/usr/bin/env python3
"""Serial port/HAT test utility for SX126x LoRa HAT.

Allows probing module settings and sending raw test data. Can optionally
control M0/M1 pins via GPIO when the HAT is on the header, or rely on
jumpers when using a USB adapter.
"""
import argparse, time, sys, os, glob

# Ensure local GPIO shim (src/RPi/GPIO.py) is available
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None

try:
    import serial
except Exception as e:
    print("Missing pyserial: pip install pyserial", file=sys.stderr)
    raise

# HAT BCM pins according to the driver
M0 = 22
M1 = 27

def detect_serial_default() -> str:
    """Return a default serial device. Prefer USB if available."""
    # Prefer USB if connected
    usb = sorted(glob.glob('/dev/ttyUSB*'))
    if usb:
        return usb[0]
    # If no USB, use Pi's UART
    return '/dev/serial0'

def set_mode(config_mode: bool, use_gpio: bool):
    """Drive M0/M1 for config or normal mode if using GPIO control."""
    if not use_gpio:
        return
    if GPIO is None:
        print("GPIO not available in this environment (use --no-gpio with USB/CP2102 or set M0/M1 with jumpers)")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(M0, GPIO.OUT)
    GPIO.setup(M1, GPIO.OUT)
    if config_mode:
        # M0=LOW, M1=HIGH => config mode
        GPIO.output(M0, GPIO.LOW)
        GPIO.output(M1, GPIO.HIGH)
    else:
        # M0=LOW, M1=LOW => normal mode
        GPIO.output(M0, GPIO.LOW)
        GPIO.output(M1, GPIO.LOW)
    time.sleep(0.5)


def probe_settings(ser: serial.Serial, timeout=1.5) -> bytes:
    """Send 0xC1 0x00 0x09 to read parameters and return raw response."""
    # Read-parameters command: 0xC1 0x00 0x09
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
    """Parse args and run serial probe/send operations for the HAT."""
    ap = argparse.ArgumentParser(description="SX126x HAT serial port test")
    ap.add_argument('--serial', default=None, help='Serial device (/dev/serial0 or /dev/ttyUSB0). Auto-detect if omitted.')
    ap.add_argument('--baud', type=int, default=9600)
    ap.add_argument('--probe', action='store_true', help='Try reading module parameters (config mode)')
    ap.add_argument('--send', default='', help="Send raw text to observe UART activity (e.g. 'HELLO\\r\\n')")
    ap.add_argument('--gpio', dest='use_gpio', action='store_true', help='Control M0/M1 via GPIO (HAT on header, no jumpers)')
    ap.add_argument('--no-gpio', dest='use_gpio', action='store_false', help='Do not control M0/M1 via GPIO (use jumpers or USB path)')
    ap.set_defaults(use_gpio=None)
    # Backward compatibility
    ap.add_argument('--skip-gpio', action='store_true', help='Alias for --no-gpio')
    ap.add_argument('--burst', type=int, default=1, help='Repeat send N times (to observe LEDs)')
    args = ap.parse_args()

    # Auto-detect port if not specified
    serial_dev = args.serial or detect_serial_default()

    # Resolve GPIO usage automatically if not specified
    if args.use_gpio is None:
        # If using USB, default to NO GPIO; if /dev/serial0, use GPIO if available
        args.use_gpio = (not serial_dev.startswith('/dev/ttyUSB')) and (GPIO is not None)
    # Honor alias --skip-gpio
    if args.skip_gpio:
        args.use_gpio = False

    # Determine desired mode for M0/M1
    config_mode = bool(args.probe)

    # Guidance messages about jumpers depending on context
    if not args.use_gpio:
        if serial_dev.startswith('/dev/ttyUSB'):
            # USB/CP2102
            if config_mode:
                print("Note: with USB and no GPIO, set jumpers: A closed; M0 closed, M1 open (config mode)")
            else:
                print("Note: with USB and no GPIO, set jumpers: A closed; M0 closed, M1 closed (normal mode)")
        else:
            print("Warning: without GPIO using /dev/serial0, ensure M0/M1 are set by jumpers (LOW/LOW for normal, LOW/HIGH for config)")

    # If probing, enter config mode; if only sending, normal mode
    set_mode(config_mode=config_mode, use_gpio=args.use_gpio)

    print(f"Opening {serial_dev} @ {args.baud} bps…")
    try:
        ser = serial.Serial(serial_dev, args.baud, timeout=0.2)
    except Exception as e:
        print(f"Error opening {serial_dev}: {e}")
        sys.exit(1)

    time.sleep(0.1)

    did = False
    if args.probe:
        did = True
        print("Probing parameters (0xC1 0x00 0x09)…")
        resp = probe_settings(ser)
        if resp.startswith(b'\xC1') and len(resp) >= 3 and resp[2] == 0x09:
            print(f"OK: response {resp.hex()}")
        else:
            print(f"No valid response (received {resp.hex() if resp else 'nothing'})")
        # Return to normal mode if controlling GPIO
        set_mode(config_mode=False, use_gpio=args.use_gpio)

    if args.send:
        did = True
        data = args.send.encode()
        print(f"Sending {len(data)} bytes x {args.burst}…")
        for i in range(max(1, args.burst)):
            ser.write(data)
            ser.flush()
            time.sleep(0.05)
        print("Sent. Observe LEDs/analyzer/receiver.")

    if not did:
        print("Nothing to do: use --probe or --send 'TEXT'")

    ser.close()

if __name__ == '__main__':
    main()
