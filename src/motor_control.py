import serial
import sys
import glob
import time

class MotorControl:
    """Class to control a motor via serial communication."""

    def __init__(self, serial_port):
        """Initialize the serial connection to the motor."""
        try:
            self.ser = serial.Serial(port=serial_port, baudrate=9600, timeout=5)  #baudrate = 9600 on our motors
            self.ser.rts=True
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
        self.numMotors = 1
        self.__read_until(b"<>\n")


    def __read_until(self, end_signal: bytes):
        """Read from the serial connection until the end signal is reached."""
        try:
            return self.ser.read_until(end_signal)
        except serial.SerialException as e:
            print(f"Failed to read from serial port: {e}")
            
    def __write_command(self, command: bytes):
        """Write a command to the serial port."""
        try:
            self.ser.write(command)
            print(f"Sent command: {command}")
        except serial.SerialException as e:
            print(f"Failed to send command: {e}")
            raise
        
    def connection_motor(self):
        """Connect to the motor."""
        command = f"CON\n"
        self.__write_command(command.encode())
    
    def move_motor(self, motor: int, direction: int, steps: int):
        """Send move command to the specified motor."""
        command = f"MOVE,{motor},{direction},{steps}\n"
        self.__write_command(command.encode())

    def set_num_motors(self, num_motors: int):
        """Set the number of motors."""
        command = f"SETMOTORS,{num_motors}\n"
        self.__write_command(command.encode())

    def stop_motor(self, motor: int):
        """Send stop command to a specified motor."""
        command = f"STOP,{motor}\n"
        self.__write_command(command.encode())

    def close(self):
        """Close the serial connection."""
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Failed to close serial port: {e}")

    def read(self):
        """Read a line from the serial connection."""
        try:
            return self.ser.readline().strip().decode("utf-8")
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
    
    for port in ports:
        try:
            with serial.Serial(port, baudrate=9600, timeout=5) as ser:  # Use 'with' to ensure the port is closed
                ser.rts=True
                start_signal = "<>".encode()
                ser.read_until(start_signal)
                try:
                    ser.write(b"CON\n")
                    com_response=ser.readline().strip().decode("utf-8")
                    if com_response == "MOTORUP":
                        return port
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError on port {port}: {e}")
        except (OSError, serial.SerialException):
            pass
    return None

if __name__ == "__main__":
    
    steps = 200

    motor_port = serial_ports()

    if motor_port is None:
        print("No motor port found")
        sys.exit(1)

    motor = MotorControl(motor_port)
    motor.connection_motor()
    print(f"READING HERE IF MOTOR IS UP --> {motor.read()}")
    motor.set_num_motors(1)
    motor.move_motor(1, 1, steps)
    time.sleep(1)
    motor.move_motor(1, 0, steps)
    time.sleep(1)
    motor.stop_motor(1)
    motor.close()
    
    


