import serial
import sys
import glob

class MotorControl:
    """Class to control a motor via serial communication."""

    def __init__(self, serial_port):
        """Initialize the serial connection to the motor."""
        try:
            self.ser = serial.Serial(port=serial_port, baudrate=115200, timeout=3)
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")

    def move(self, left, right):
        """Send move command to the motor."""
        try:
            self.ser.write(f"M{left} {right}\n")
        except serial.SerialException as e:
            print(f"Failed to send move command: {e}")

    def stop(self):
        """Send stop command to the motor."""
        try:
            self.ser.write("S\n")
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

    


