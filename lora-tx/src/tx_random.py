#!/usr/bin/env python3
import os, argparse, json, random, time
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--serial', default=os.getenv('SERIAL','/dev/serial0'))
    ap.add_argument('--freq', type=int, default=int(os.getenv('FREQ','915')))
    ap.add_argument('--addr', type=int, default=int(os.getenv('ADDR','101')))
    ap.add_argument('--dest', type=int, default=int(os.getenv('DEST','65535')))
    ap.add_argument('--power', type=int, default=int(os.getenv('POWER','22')))
    ap.add_argument('--airspeed', type=int, default=int(os.getenv('AIRSPEED','2400')))
    ap.add_argument('--mode', choices=['json','text'], default=os.getenv('MODE','json'))
    ap.add_argument('--period', type=float, default=float(os.getenv('PERIOD','1.0')))
    args = ap.parse_args()

    dev = sx126x(serial_num=args.serial, freq=args.freq, addr=args.addr,
                 power=args.power, rssi=False, air_speed=args.airspeed, relay=False)

    seq = 0
    print(f"TX → dest={hex(args.dest)} @ {args.freq}.125 MHz | mode={args.mode} | period={args.period}s")
    try:
        while True:
            if args.mode == 'json':
                payload_obj = {'ts': now_iso(), 'seq': seq,
                               'rand': random.randint(0, 10**6),
                               'val': round(random.uniform(0,100), 3)}
                payload = json.dumps(payload_obj, separators=(',',':')).encode()
            else:
                payload = f"MSG|{seq:06d}|{now_iso()}|{random.randint(0,9999)}".encode()

            frame = build_frame(dev, args.dest, payload)
            dev.send(frame)
            print("TX:", payload.decode(errors='ignore'))
            seq += 1
            time.sleep(args.period)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
