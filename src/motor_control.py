import serial
import sys
import glob
import time
import numpy as np

# Constants
STEPS_PER_REV = 200  # for a 1.8° stepper motor

class MotorControl:
    """Class to control a motor via serial communication."""

    def __init__(self, serial_port :str, 
                 motor_relation: float, 
                 motor_microstep: int, 
                 motor_start: float, 
                 motor_end: float, 
                 motor_step_size: float,
                 motor_name: str,
                 motor_id: int) -> None:
        """Initialize the serial connection to the motor."""
        print(f"Initializing motor '{motor_name}'...")
        self.initialize_serial(serial_port)
        self.configure_motor(motor_relation, motor_microstep, motor_start, motor_end, 
                             motor_step_size, motor_name, motor_id)

    def initialize_serial(self, serial_port: str):
        """Initialize serial connection with robust error handling."""
        try:
            self.ser = serial.Serial(port=serial_port, baudrate=9600, timeout=5)
            self.ser.rts = True
            self.__read_until(b"<>\n")
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            sys.exit(1)  # Exit if serial connection fails
            
    def configure_motor(self, motor_relation: float,
                        motor_microstep: int,
                        motor_start: float,
                        motor_end: float,
                        motor_step_size: float,
                        motor_name: str,
                        motor_id: int) -> None:
        """Configure motor parameters and initialize position."""
        # Motor parameters for step-wise movement
        self.motor_relation = motor_relation
        self.motor_microstep = motor_microstep # 1 for full step, 2 for half step, etc.
        self.motor_start = motor_start
        self.motor_end = motor_end  
        self.motor_step_size = motor_step_size 
        self.current_position_mm = self.motor_start  # Initialize at start position
        self.total_steps_required = 0
        self.steps_moved = 0
        self.motor_name = motor_name
        self.motor_id = motor_id
    
    def __read_until(self, end_signal: bytes) -> bytes:
        """Read from the serial connection until the end signal is reached."""
        try:
            return self.ser.read_until(end_signal)
        except serial.SerialException as e:
            print(f"Failed to read from serial port: {e}")
            
    def __write_command(self, command: bytes) -> None:
        """Write a command to the serial port and wait for an 'F' response."""
        try:
            self.ser.write(command)
            print(f"Sent command: {command}")
            # Wait for an 'F', make it sequential
            response = ''
            while not response.endswith('F'):
                response += self.ser.read_until(b'F').decode().strip() 
            print(f"Received response: {response}")
        except serial.SerialException as e:
            print(f"Failed to send command: {e}")
            raise

    def connection_motor(self) -> None:
        """Connect to the motor."""
        command = f"CON\n"
        self.__write_command(command.encode())
    
    def move_motor(self, direction: int, steps: int) -> None:
        """Send move command to the specified motor."""
        command = f"MOVE,{self.motor_id},{direction},{steps}\n"
        self.__write_command(command.encode())
        
    def move_motor_to(self, position: int) -> None:
        """Send move command to the specified motor."""
        command = f"MOVETO,{self.motor_id},{position}\n"
        self.__write_command(command.encode())
        self.current_position_mm = position * self.motor_relation / STEPS_PER_REV / self.motor_microstep

    def set_num_motors(self, num_motors: int) -> None:
        """Set the number of motors."""
        command = f"SETMOTORS,{num_motors}\n"
        self.__write_command(command.encode())

    def stop_motor(self) -> None:
        """Send stop command to a specified motor."""
        command = f"STOP,{self.motor_id}\n"
        self.__write_command(command.encode())
    
    def pingLED(self) -> None:
        """Send a ping to the LED."""
        command = f"LED\n"
        self.__write_command(command.encode())

    def close(self) -> None:
        """Close the serial connection."""
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Failed to close serial port: {e}")

    def read(self) -> str:
        """Read a line from the serial connection."""
        try:
            return self.ser.readline().strip().decode("utf-8")
        except serial.SerialException as e:
            print(f"Failed to read from serial port: {e}")
            
    def move_to_start(self) -> None:
        """Prepare motor for step-wise movement."""
        # Move to starting position if necessary (This assumes absolute positioning)
        # You might need to reset or track the position if the motor doesn't have absolute positioning
        self.move_to_position(self.motor_start)
    
    def move_to_home(self) -> None:
        """Move motor to the home position."""
        self.move_motor_to(0)
        self.steps_moved = 0  # Reset step count after moving to home position
        self.current_position_mm = 0.0
        print(f"Motor moved to HOME position.")

    def move_to_position(self, position_mm: float) -> None:
        """Move motor to a specific position."""        
        # Calculate steps needed to reach the position
        target_revs = position_mm / self.motor_relation
        target_steps = int(target_revs * STEPS_PER_REV * self.motor_microstep)
        steps_needed = target_steps - self.steps_moved

        if steps_needed != 0:
            self.move_motor(1 if steps_needed > 0 else -1, abs(steps_needed))
            self.steps_moved += steps_needed
            self.current_position_mm = position_mm

    def next_step(self) -> None:
        """Move motor to the next step."""
        if self.current_position_mm < self.motor_end:
            next_position = self.current_position_mm + self.motor_step_size
            self.move_to_position(next_position )
        else:
            print("Reached the end position.")
    
    def mm_to_steps(self, position_mm: float) -> int:
        """Convert mm to steps."""
        target_revs = position_mm / self.motor_relation
        target_steps = int(target_revs * STEPS_PER_REV * self.motor_microstep)
        return target_steps 
    
    def array_of_positions(self) -> np.array:
        """Create an array of absolute positions."""
        positions_mm = np.arange(self.motor_start, self.motor_end + self.motor_step_size, self.motor_step_size)
        return positions_mm           
        
def serial_ports() -> str:
    """Lists serial port names.

    :raises EnvironmentError: On unsupported or unknown platforms
    :returns: A list of the serial ports available on the system
    """
    print("Searching for motor port...")
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
                        print(f"Motor found on port {port}")
                        return port
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError on port {port}: {e}")
        except (OSError, serial.SerialException):
            pass
    return None

if __name__ == "__main__":
    # Find the motor port
    motor_port = serial_ports()

    if motor_port is None:
        print("No motor port found")
        sys.exit(1)

    motor = MotorControl(motor_port, 0.5, 1, 3.0, 1.0, -0.25, "motorX", 1)
    
    
    # Create an array of absolute positions
    positions_mm = np.arange(motor.motor_start, motor.motor_end + motor.motor_step_size, motor.motor_step_size)
    
    # Move the motor to each position
    for position_mm in [1.1, 0.5, 2.3, 4.5]:
        motor.move_motor_to(motor.mm_to_steps(position_mm))
        print(f"Motor moved to {motor.current_position_mm}mm")
    motor.move_to_home()
    print(f"Motor moved to {motor.current_position_mm}mm")
    motor.close()
    
    """
    
    motor.move_to_start()

    # Loop to move motor step by step
    while motor.current_position_mm < motor.motor_end:
        # Move motor to the next step
        motor.next_step()
        
        # Execute other commands here
        # ...
        print(f"Motor moved to {motor.current_position_mm}mm")
        # Add a delay or wait for user input or signal from other script as needed
        time.sleep(1)
    motor.move_to_home()
    print(f"Motor moved to {motor.current_position_mm}mm")
    motor.close()  # Close the motor port when done
    """
    
    


