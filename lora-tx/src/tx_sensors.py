#!/usr/bin/env python3
import os, argparse, json, random, time, math
from datetime import datetime, timezone
from dotenv import load_dotenv
from sx126x import sx126x

load_dotenv()

def build_frame(dev, dest_addr: int, payload: bytes) -> bytes:
    dest_hi = (dest_addr >> 8) & 0xFF; dest_lo = dest_addr & 0xFF
    src_hi  = (dev.addr >> 8) & 0xFF;  src_lo  = dev.addr & 0xFF
    return bytes([dest_hi, dest_lo, dev.offset_freq, src_hi, src_lo, dev.offset_freq]) + payload

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def simulate_rain(period_s: float, bucket_mm: float, total_mm: float, tips: int):
    # Simula intensidad en mm/h (0 la mayor parte del tiempo, con eventos aleatorios)
    if random.random() < 0.85:
        intensity = 0.0
    else:
        intensity = round(random.uniform(0.2, 30.0), 2)  # llovizna a lluvia moderada
    mm_this = intensity * (period_s / 3600.0)
    # Redondear por baldeos
    new_tips = int((mm_this + (total_mm - tips * bucket_mm)) // bucket_mm)
    if new_tips < 0: new_tips = 0
    total_mm += new_tips * bucket_mm
    tips += new_tips
    return {
        'intensity_mm_h': round(intensity, 3),
        'bucket_mm': bucket_mm,
        'bucket_tips_total': tips,
        'rain_mm_total': round(total_mm, 3)
    }, total_mm, tips

def simulate_seismic():
    # Simula aceleración en g con ruido ambiental
    ax = random.gauss(0.0, 0.005)
    ay = random.gauss(0.0, 0.005)
    az = random.gauss(0.0, 0.005)
    pga_g = max(abs(ax), abs(ay), abs(az))
    rms_g = math.sqrt((ax*ax + ay*ay + az*az) / 3.0)
    return {
        'ax_g': round(ax, 5),
        'ay_g': round(ay, 5),
        'az_g': round(az, 5),
        'pga_g': round(pga_g, 5),
        'rms_g': round(rms_g, 5)
    }

def main():
    ap = argparse.ArgumentParser(description='TX de datos de lluvia y sísmicos')
    ap.add_argument('--serial', default=os.getenv('SERIAL','/dev/serial0'))
    ap.add_argument('--freq', type=int, default=int(os.getenv('FREQ','915')))
    ap.add_argument('--addr', type=int, default=int(os.getenv('ADDR','101')))
    ap.add_argument('--dest', type=int, default=int(os.getenv('DEST','65535')))
    ap.add_argument('--power', type=int, default=int(os.getenv('POWER','22')))
    ap.add_argument('--airspeed', type=int, default=int(os.getenv('AIRSPEED','2400')))
    ap.add_argument('--period', type=float, default=float(os.getenv('PERIOD','1.0')))
    ap.add_argument('--station', default=os.getenv('STATION','tx01'))
    ap.add_argument('--rain', action='store_true', help='Incluir bloque de lluvia')
    ap.add_argument('--seismic', action='store_true', help='Incluir bloque sísmico')
    ap.add_argument('--bucket-mm', type=float, default=float(os.getenv('BUCKET_MM','0.2')))
    args = ap.parse_args()

    # Si no se especifica ninguno, incluir ambos por defecto
    include_rain = args.rain or (not args.rain and not args.seismic)
    include_seis = args.seismic or (not args.rain and not args.seismic)

    dev = sx126x(serial_num=args.serial, freq=args.freq, addr=args.addr,
                 power=args.power, rssi=False, air_speed=args.airspeed, relay=False)

    seq = 0
    total_mm = 0.0
    tips = 0
    print(f"TX sensors → dest={hex(args.dest)} @ {args.freq}.125 MHz | period={args.period}s | serial={args.serial}")
    try:
        while True:
            payload_obj = {
                'ts': now_iso(),
                'seq': seq,
                'station': args.station
            }
            if include_rain:
                rain_obj, total_mm, tips = simulate_rain(args.period, args.bucket_mm, total_mm, tips)
                payload_obj['rain'] = rain_obj
            if include_seis:
                payload_obj['seismic'] = simulate_seismic()

            payload = json.dumps(payload_obj, separators=(',',':')).encode()
            frame = build_frame(dev, args.dest, payload)
            dev.send(frame)
            print("TX sensors:", payload.decode(errors='ignore'))
            seq += 1
            time.sleep(args.period)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
