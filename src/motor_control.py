import serial
import sys
import glob
import numpy as np
import logging
import time
import os

from src.config import MotorConfig

# Constants
STEPS_PER_REV = 200  # for a 1.8° stepper motor
BAUDRATE = 9600
TIMEOUT = 5
__WHILE_TIMEOUT = 300  # 5 minutes timeout for while loops unused


class MotorControl:
    """Class to control a motor via serial communication."""

    # Create a logger at the class level
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Check if the logger has handlers
    if not logger.handlers:
        # Create a console handler with level DEBUG
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

    def __init__(
        self,
        serial: serial.Serial,
        motor_config: MotorConfig,
        motor_name: str,
        motor_id: int,
    ) -> None:
        """Initialize the serial connection to the motor."""
        print(f"Initializing motor '{motor_name}'...")
        self.ser = serial
        self.configure_motor(motor_config, motor_name, motor_id)
        self.connection_motor()
        print(f"Motor '{motor_name}' initialized.")

    def configure_motor(
        self,
        motor_config: MotorConfig,
        motor_name: str,
        motor_id: int,
    ) -> None:
        """Configure motor parameters and initialize position."""
        # Motor parameters for step-wise movement
        self.motor_type = motor_config.type
        self.motor_relation = motor_config.relation
        self.motor_microstep = (
            motor_config.microstep
        )  # 1 for full step, 2 for half step, etc.
        self.motor_start = motor_config.start
        self.motor_end = motor_config.end
        self.motor_step_size = motor_config.step_size
        self.while_timeout = motor_config.while_timeout
        self.current_position = self.motor_start  # Initialize at start position
        self.total_steps_required = 0
        self.steps_moved = 0
        self.motor_name = motor_name
        self.motor_id = motor_id
        self.set_acceleration(motor_config.acceleration)
        self.set_speed(motor_config.speed)
        self.set_max_speed(motor_config.max_speed)

    def _write_command(self, command: bytes) -> None:
        """Write a command to the serial port and wait for an 'F' response."""
        try:
            self.ser.write(command)
            self.logger.debug(f"Sent command: {command}")
            # Wait for an 'F', make it sequential
            start_time = time.time()
            response = ""
            while not response.endswith("F"):
                if time.time() - start_time > self.while_timeout:
                    self.logger.error("Timeout waiting for response")
                    raise TimeoutError("Timeout waiting for response from motor")
                response += self.ser.read_until(b"F").decode().strip()
            self.logger.debug(f"Received response: {response}")
        except serial.SerialException as e:
            self.logger.error(f"Failed to send command: {e}")
            raise

    def _format_command(self, *args) -> bytes:
        """Format a command to send to the motor."""
        return ",".join(str(arg) for arg in args).encode()

    def connection_motor(self) -> None:
        """Connect to the motor."""
        command = self._format_command("CON")
        self._write_command(command)

    def set_speed(self, speed: int) -> None:
        """Set the speed."""
        command = self._format_command("SET_SPEED", self.motor_id, speed)
        self._write_command(command)
        self.logger.info(f"Motor {self.motor_name} speed set to {speed}")

    def set_max_speed(self, max_speed: int) -> None:
        """Set the maximum speed."""
        command = self._format_command("SET_MAX_SPEED", self.motor_id, max_speed)
        self._write_command(command)
        self.logger.info(f"Motor {self.motor_name} max speed set to {max_speed}")

    def set_acceleration(self, acceleration: int) -> None:
        """Set the acceleration."""
        command = self._format_command("SET_ACCEL", self.motor_id, acceleration)
        self._write_command(command)
        self.logger.info(f"Motor {self.motor_name} acceleration set to {acceleration}")

    def move_motor(self, direction: int, steps: int) -> None:
        """Send move command (mm or degrees) to the specified motor."""
        print(
            f"Moving {self.motor_name} {'forward' if direction > 0 else 'backward'} by {steps} steps..."
        )
        command = self._format_command("MOVE", self.motor_id, direction, steps)
        self._write_command(command)

    def move_motor_to(self, steps: int) -> None:
        """Send move to command (mm or degrees) to the specified motor."""
        print(f"Moving {self.motor_name} to {steps} steps...")
        command = self._format_command("MOVETO", self.motor_id, steps)
        self._write_command(command)

    def stop_motor(self) -> None:
        """Send stop command to a specified motor."""
        command = self._format_command("STOP", self.motor_id)
        self._write_command(command)

    def pingLED(self) -> None:
        """Send a ping to the LED."""
        command = self._format_command("LED")
        self._write_command(command)

    def find_home(self) -> None:
        """Find the home position."""
        command = self._format_command(
            "MOVE", self.motor_id, -1, 1000000
        )  # Move motor to the home position
        print(f"Searching for {self.motor_name} to HOME position...")
        self._write_command(command)
        self.current_position = 0.0
        self.steps_moved = 0  # Reset step count after moving to home position

        # Send the SET_ZERO command to set absolute position to 0
        command = self._format_command("SET_ZERO", self.motor_id)
        self._write_command(command)
        print(f"Motor moved to HOME position.")

    def move_to_home(self) -> None:
        """Move motor to the home position."""
        print(f"Moving {self.motor_name} to HOME position...")
        self.move_motor_to(0)
        self.steps_moved = 0  # Reset step count after moving to home position
        self.current_position = 0.0
        print(f"Motor moved to HOME position.")

    def position_to_steps(self, position: float) -> int:
        """Convert the position (mm or degrees) into steps."""
        self.current_position = position  # Update current position
        if self.motor_type == "linear":
            target_revs = position / self.motor_relation
        elif self.motor_type == "rotatory":
            degrees_per_rev = 360
            target_revs = (
                position / degrees_per_rev * self.motor_relation
            )  # looks like there is a 10:1 gear ratio in the rotor motor
        else:
            raise ValueError(f"Motor type {self.motor_type} unknown.")
        target_steps = int(target_revs * STEPS_PER_REV * self.motor_microstep)
        return target_steps

    def array_of_positions(self) -> np.array:
        """Create an array of absolute positions (mm or degrees)."""
        positions = np.arange(
            self.motor_start,
            self.motor_end + self.motor_step_size,
            self.motor_step_size,
        )
        return positions

    def close(self) -> None:
        """Close the serial connection."""
        try:
            self.ser.close()
        except serial.SerialException as e:
            print(f"Failed to close serial port: {e}")


def find_serial_port(COM_port: str = "") -> serial.Serial:
    """Find the motor serial connection and return it.

    :param COM_port: The COM port to connect to (default is "")
    :raises EnvironmentError: On unsupported or unknown platforms
    :returns: a serial.Serial object with the motor connection open and ready
    to use for communication
    """
    logger = logging.getLogger(__name__)
    logger.info("Searching for motor port...")
    if COM_port:
        ports = [COM_port]
    else:
        if sys.platform.startswith("win"):
            ports = [f"COM{i + 1}" for i in range(256)]
        elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
            ports = glob.glob("/dev/tty[A-Za-z]*")
        elif sys.platform.startswith("darwin"):
            ports = glob.glob("/dev/tty.*")
        else:
            raise EnvironmentError("Unsupported platform")

    for port in ports:
        try:
            # Change the permissions of the port to read and write
            if not sys.platform.startswith("win"):
                os.system(f"sudo chmod a+rw {port}")

            ser = serial.Serial(port, baudrate=BAUDRATE, timeout=TIMEOUT)
            ser.rts = True
            start_signal = "<>".encode()
            ser.read_until(start_signal)
            try:
                ser.write(b"CON\n")
                com_response = ser.readline().strip().decode("utf-8")
                if com_response == "MOTORUP":
                    logger.info(f"Motor found on port {port}")
                    return ser
            except UnicodeDecodeError as e:
                logger.error(f"UnicodeDecodeError on port {port}: {e}")
                ser.close()  # Close the port in case of an error
        except (OSError, serial.SerialException) as e:
            logger.debug(f"Failed to connect to port {port}: {e}")
    logger.warning("No motor port found. \nPlease connect the motor and try again.")
    sys.exit(1)  # Exit if serial connection fails


if __name__ == "__main__":
    pass
