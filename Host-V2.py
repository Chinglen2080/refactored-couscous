import serial
import struct
import time

sensor_data_format = 'llibb'  
sensor_data_size = struct.calcsize(sensor_data_format)

def log_session_start(mode):
    line = f"
=== New session started using {mode.upper()} mode at {time.strftime('%Y-%m-%d %H:%M:%S')} ==="
    print(line)  # Print to console
    with open("logs.txt", "a") as f:
        f.write(line + "
")

def on_detect_sensor1(formatted_time):
    with open("logs.txt", "a") as f:
        f.write(f"Object detected at sensor 1 at {formatted_time}.
")

def on_detect_sensor2(formatted_time):
    with open("logs.txt", "a") as f:
        f.write(f"Object detected at sensor 2 at {formatted_time}.
")

def on_out_of_range(formatted_time):
    with open("logs.txt", "a") as f:
        f.write(f"Object out of range at {formatted_time}.
")

def on_servo_move(angle, formatted_time):
    with open("logs.txt", "a") as f:
        f.write(f"Servo moved to {angle}° at {formatted_time}.
")

def on_siren_change(state, formatted_time):
    with open("logs.txt", "a") as f:
        f.write(f"Siren turned {'ON' if state else 'OFF'} at {formatted_time}.
")

def on_sensor_data(sensor_dict, formatted_time):
    log_line = f"[{formatted_time}] Wireless data: {sensor_dict}
"
    print(log_line.strip())
    with open("logs.txt", "a") as f:
        f.write(log_line)

def parse_sensor_data(binary_data):
    unpacked = struct.unpack(sensor_data_format, binary_data)
    return {
        'distance1': unpacked[0],
        'distance2': unpacked[1],
        'servoAngle': unpacked[2],
        'activeSensor': unpacked[3],
        'siren': bool(unpacked[4]),
        'flash': bool(unpacked[5])
    }

def main():
    mode = input("Select connection mode (wired/wireless): ").strip().lower()
    if mode not in ['wired', 'wireless']:
        print("Invalid mode selected.")
        return

    log_session_start(mode)

    port = input("Enter serial port (e.g. COM3 or /dev/ttyUSB0): ").strip()
    baudrate = 9600
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)

    buffer = bytearray()
    last_servo_angle = None
    last_siren_state = None
    last_active_sensor = None

    try:
        while True:
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if mode == 'wired':
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                print(line)

                if line.startswith("Event:"):
                    if "Sensor 1 detected" in line and last_active_sensor != 1:
                        on_detect_sensor1(formatted_time)
                        last_active_sensor = 1
                    elif "Sensor 2 detected" in line and last_active_sensor != 2:
                        on_detect_sensor2(formatted_time)
                        last_active_sensor = 2
                    elif "No object detected" in line and last_active_sensor != 0:
                        on_out_of_range(formatted_time)
                        last_active_sensor = 0
                    elif "Servo moved to" in line:
                        try:
                            angle = int(line.split("Servo moved to")[1].split("degrees")[0].strip())
                            if angle != last_servo_angle:
                                on_servo_move(angle, formatted_time)
                                last_servo_angle = angle
                        except:
                            pass
                    elif "Siren activated" in line and last_siren_state != True:
                        on_siren_change(True, formatted_time)
                        last_siren_state = True
                    elif "Siren deactivated" in line and last_siren_state != False:
                        on_siren_change(False, formatted_time)
                        last_siren_state = False

            elif mode == 'wireless':
                while len(buffer) < sensor_data_size:
                    new_bytes = ser.read(sensor_data_size - len(buffer))
                    if not new_bytes:
                        break
                    buffer.extend(new_bytes)

                if len(buffer) >= sensor_data_size:
                    sensor_packet = buffer[:sensor_data_size]
                    buffer = buffer[sensor_data_size:]
                    sensor_dict = parse_sensor_data(sensor_packet)
                    on_sensor_data(sensor_dict, formatted_time)

                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"Backup serial line: {line}")

    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        ser.close()

if __name__ == '__main__':
    main()