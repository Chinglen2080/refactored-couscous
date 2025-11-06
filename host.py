import serial
import time
import re

def on_detect_sensor1(distance):
    pass  # Blank function for sensor 1 detection event

def on_detect_sensor2(distance):
    pass  # Blank function for sensor 2 detection event

def on_out_of_range():
    pass  # Blank function when no sensors detect anything

def on_siren_active():
    pass  # Blank function for siren active event

def on_idle():
    pass  # Blank function for idle state

def parse_serial_line(line):
    match = re.match(r"D1:s*(d+)s*|s*D2:s*(d+)", line)
    if match:
        d1 = int(match.group(1))
        d2 = int(match.group(2))
        return d1, d2
    return None, None

def main(port='COM3', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)
    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            d1, d2 = parse_serial_line(line)
            if d1 is None or d2 is None:
                continue

            sensor1_detected = d1 <= 20
            sensor2_detected = d2 <= 15

            if sensor1_detected and d1 < d2:
                on_detect_sensor1(d1)
                on_idle()
            elif sensor2_detected:
                on_detect_sensor2(d2)
                on_siren_active()
            else:
                on_out_of_range()
                on_idle()

    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

if __name__ == '__main__':
    main()
