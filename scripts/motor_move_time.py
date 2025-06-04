#!/usr/bin/env python3

"""
Move the motor to the desired position.

Usage:
    motor_move_time.py <YAMLCONF> <motorname> <motion_time_s> <direction>

Arguments:
    YAMLCONF       File with all parameters to take into account in the scan.
    motorname      Name of the motor to move. Must be motorX, motorY or motorZ.
    motion_time_s  Desired motion time for the motor in seconds.
    direction      Direction to move the motor. Must be 1 (forward) or 0 (backward).

Options:
    -h --help     Show this screen.
"""

from docopt import docopt
import yaml
from src.config import MotorConfig, validate_yaml_dict

from src.motor_control import MotorControl
from src.motor_control import find_serial_port


def time_to_steps(motor_speed: float, motion_time_s: float) -> int:
    """
    Calculate the number of steps required for the motor to move in the given time.
    """
    return int(motion_time_s * motor_speed)


if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["<YAMLCONF>"]
    motor_name = args["<motorname>"]
    motion_time_s = float(args["<motion_time_s>"])
    direction = int(args["<direction>"])

    # Check that the direction is valid
    if direction not in [0, 1]:
        raise ValueError(f"Direction {direction} is not valid. Must be 1 or 0.")

    direction = -1 if direction == 0 else 1
    # Check that the motor name is valid
    if motor_name not in ["motorX", "motorY", "motorZ"]:
        raise ValueError(
            f"Motor name {motor_name} is not valid. Must be motorX, motorY or motorZ."
        )

    # Load the YAML configuration file
    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)

    # Validate the YAML configuration file
    validate_yaml_dict(yaml_dict)

    # Find the motor port
    com_port = yaml_dict["COM_port"]
    motors_serial = find_serial_port(com_port)

    # Create a MotorControl instance for each motor
    motors = []
    for i in range(yaml_dict["num_motors"]):
        motor_name_loop = f"motor{chr(88 + i)}"  # 88 is ASCII for 'X'
        motor_config = MotorConfig(
            yaml_dict[motor_name_loop], int(motion_time_s + 60)
        )  # Add 60 seconds to the motion time for safety
        motor = MotorControl(motors_serial, motor_config, motor_name_loop, i + 1)
        motors.append(motor)

    # Move the motor to the desired position
    for motor in motors:
        if motor.motor_name == motor_name:
            # Convert the motion time in seconds to steps
            steps = time_to_steps(yaml_dict["motorX"]["speed"], motion_time_s)
            motor.move_motor(direction, steps)
            motor.close()
