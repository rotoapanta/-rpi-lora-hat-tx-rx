import lgpio, atexit

BCM, BOARD = 11, 10
IN, OUT = 1, 0
LOW, HIGH = 0, 1

_chip = None
_claimed = set()

def _ensure():
    global _chip
    if _chip is None:
        _chip = lgpio.gpiochip_open(0)  # gpiochip0 en Raspberry Pi
        atexit.register(cleanup)

def setmode(mode):  # compat
    pass

def setwarnings(flag):  # compat
    pass

def setup(pin, direction, initial=None):
    _ensure()
    if direction == OUT:
        lgpio.gpio_claim_output(_chip, pin, HIGH if initial else LOW if initial is not None else LOW)
    else:
        lgpio.gpio_claim_input(_chip, pin)
    _claimed.add(pin)

def output(pin, value):
    _ensure()
    lgpio.gpio_write(_chip, pin, HIGH if value else LOW)

def input(pin):
    _ensure()
    return lgpio.gpio_read(_chip, pin)

def cleanup(pin=None):
    global _chip
    if _chip is None: return
    if pin is None:
        for p in list(_claimed):
            try: lgpio.gpio_free(_chip, p)
            except Exception: pass
        _claimed.clear()
        lgpio.gpiochip_close(_chip); _chip = None
    else:
        if pin in _claimed:
            try: lgpio.gpio_free(_chip, pin)
            except Exception: pass
            _claimed.discard(pin)
