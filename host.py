import serial
import time

def on_detect_sensor1():
    with open("logs.txt", "a") as f:
        f.write(f"Object detected at sensor 1 at {formatted_time}.\n")
    
def on_detect_sensor2():
    with open("logs.txt", "a") as f:
        f.write(f"Object detected at sensor 2 at {formatted_time}.\n")

def on_out_of_range():
    with open("logs.txt", "a") as f:
        f.write(f"Object out of range at {formatted_time}.\n")

def on_servo_move(angle):
    with open("logs.txt", "a") as f:
        f.write(f"Servo moved to {angle}° at {formatted_time}.\n")

def on_siren_change(state):
    with open("logs.txt", "a") as f:
        f.write(f"Siren turned {state} at {formatted_time}.\n")

def on_status(status_dict):
    print(status_dict)

def parse_status(line):
    print(line)

def main(port='COM3', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Allow Arduino reset

    last_servo_angle = None
    last_siren_state = None
    last_active_sensor = None

    try:
        while True:
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time_struct)
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
