#!/usr/bin/env python3
import os, argparse, time, csv
from dotenv import load_dotenv
from sx126x import sx126x

load_dotenv()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--serial', default=os.getenv('SERIAL','/dev/serial0'))
    ap.add_argument('--freq', type=int, default=int(os.getenv('FREQ','915')))
    ap.add_argument('--addr', type=int, default=int(os.getenv('ADDR','0')))
    ap.add_argument('--power', type=int, default=int(os.getenv('POWER','22')))
    ap.add_argument('--airspeed', type=int, default=int(os.getenv('AIRSPEED','2400')))
    ap.add_argument('--csv', default=os.getenv('RX_CSV',''))
    ap.add_argument('--debug', type=int, default=int(os.getenv('RX_DEBUG','0')))
    args = ap.parse_args()

    debug = bool(args.debug)

    dev = sx126x(serial_num=args.serial, freq=args.freq, addr=args.addr,
                 power=args.power, rssi=True, air_speed=args.airspeed, relay=False)

    writer = None; f = None
    if args.csv.strip():
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        f = open(args.csv, 'a', newline='')
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(['ts','src_addr','freq_mhz','payload'])

    print(f"RX @ {args.freq}.125 MHz | serial={args.serial} | air={args.airspeed}bps (CTRL+C para salir)")
    try:
        while True:
            if dev.ser.inWaiting() > 0:
                time.sleep(0.5)
                to_read = dev.ser.inWaiting()
                r = dev.ser.read(to_read)
                if debug:
                    print(f"DEBUG raw len={len(r)} data={r.hex()}")
                
                min_len = 4 + (1 if dev.rssi else 0)
                if len(r) < min_len:  # demasiado corto para contener addr, canal y payload
                    continue
                
                src_addr = (r[0] << 8) + r[1]
                freq_mhz = dev.start_freq + r[2]
                payload = r[3:-1] if dev.rssi else r[3:]
                try:
                    text = payload.decode()
                except Exception:
                    text = payload.hex()
                ts = time.strftime('%Y-%m-%dT%H:%M:%S')
                print(f"RX {ts} | src={src_addr} @ {freq_mhz}.125 MHz | {text}")
                if writer:
                    writer.writerow([ts, src_addr, f"{freq_mhz}.125", text]); f.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        if f: f.close()

if __name__ == '__main__':
    main()
