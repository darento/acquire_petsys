import serial
import sys
import glob

class MotorControl:
    """Class to control a motor via serial communication."""

    def __init__(self, serial_port):
        """Initialize the serial connection to the motor."""
        try:
            self.ser = serial.Serial(port=serial_port, baudrate=9600, timeout=3)  #baudrate = 9600 on our motors
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
        self.numMotors = 1

    def move_motor(self, motor: int, direction: int, steps: int):
        """Send move command to the specified motor."""
        command = f"MOVE,{motor},{direction},{steps}\n"
        try:
            self.ser.write(command.encode())
        except serial.SerialException as e:
            print(f"Failed to send move command: {e}")

    def set_num_motors(self, num_motors: int):
        """Set the number of motors."""
        command = f"SETMOTORS,{num_motors}\n"
        try:
            self.ser.write(command.encode())
        except serial.SerialException as e:
            print(f"Failed to send set_num_motors command: {e}")

    def stop_motor(self, motor: int):
        """Send stop command to a specified motor."""
        command = f"STOP,{motor}\n"
        try:
            self.ser.write(command.encode())
        except serial.SerialException as e:
            print(f"Failed to send stop command: {e}")

    def close(self):
        """Close the serial connection."""
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Failed to close serial port: {e}")

    def read(self):
        """Read a line from the serial connection."""
        try:
            return self.ser.readline()
        except serial.SerialException as e:
            print(f"Failed to read from serial port: {e}")

def serial_ports():
    """Lists serial port names.

    :raises EnvironmentError: On unsupported or unknown platforms
    :returns: A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = [f'COM{i + 1}' for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <number of steps>")
        sys.exit(1)

    steps = int(sys.argv[1])

    ports = serial_ports()


    print(ports)
    exit(0)

    if len(ports) == 0:
        print("No serial ports found")
        sys.exit(1)

    motor = MotorControl(ports[0])
    motor.move(steps)
    motor.close()

    


