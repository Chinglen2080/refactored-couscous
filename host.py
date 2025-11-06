import serial
import time

def on_detect_sensor1():
    pass  # Blank function for sensor 1 detection event

def on_detect_sensor2():
    pass  # Blank function for sensor 2 detection event

def on_out_of_range():
    pass  # Blank function for no detection event

def on_servo_move(angle):
    pass  # Blank function for servo angle change

def on_siren_change(state):
    pass  # Blank function for siren on/off

def on_status(status_dict):
    pass  # Blank function for periodic status update

def parse_status(line):
    # Parse status line of format:
    # Status | D1: 15 cm, D2: 20 cm, Servo: 45°, LEDs [OR:1, RED:0, BLU:0, COL:0], Siren: ON
    try:
        parts = line.split('|')[1].strip()
        parts_dict = {}
        segments = parts.split(',')
        for segment in segments:
            segment = segment.strip()
            if segment.startswith("D1:"):
                parts_dict['d1'] = int(segment.split()[1])
            elif segment.startswith("D2:"):
                parts_dict['d2'] = int(segment.split()[1])
            elif segment.startswith("Servo:"):
                parts_dict['servo'] = int(segment.split()[1].replace("°", ""))
            elif segment.startswith("LEDs"):
                # Extract LED values
                led_states = segment.split('[')[1].split(']')[0].split(',')
                led_dict = {}
                for led_state in led_states:
                    key, value = led_state.split(':')
                    led_dict[key.strip()] = int(value.strip())
                parts_dict['leds'] = led_dict
            elif segment.startswith("Siren:"):
                parts_dict['siren'] = segment.split()[1].upper() == 'ON'
        return parts_dict
    except Exception:
        return None

def main(port='COM3', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Allow Arduino reset

    last_servo_angle = None
    last_siren_state = None
    last_active_sensor = None

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            print(line)  # For debugging

            # Check for event lines
            if line.startswith("Event:"):
                if "Sensor 1 detected" in line:
                    if last_active_sensor != 1:
                        on_detect_sensor1()
                        last_active_sensor = 1
                elif "Sensor 2 detected" in line:
                    if last_active_sensor != 2:
                        on_detect_sensor2()
                        last_active_sensor = 2
                elif "No object detected" in line:
                    if last_active_sensor != 0:
                        on_out_of_range()
                        last_active_sensor = 0
                elif "Servo moved to" in line:
                    try:
                        angle = int(line.split("Servo moved to")[1].split("degrees")[0].strip())
                        if angle != last_servo_angle:
                            on_servo_move(angle)
                            last_servo_angle = angle
                    except:
                        pass
                elif "Siren activated" in line:
                    if last_siren_state != True:
                        on_siren_change(True)
                        last_siren_state = True
                elif "Siren deactivated" in line:
                    if last_siren_state != False:
                        on_siren_change(False)
                        last_siren_state = False

            # Check for status lines
            elif line.startswith("Status"):
                status = parse_status(line)
                if status:
                    on_status(status)

    except KeyboardInterrupt:
        print("Exiting")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
