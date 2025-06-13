#!/usr/bin/env python3

"""
Move the motor to the desired position.

Usage:
    move_to.py <YAMLCONF> <motorname> <position_mm> <direction>

Arguments:
    YAMLCONF     File with all parameters to take into account in the scan.
    motorname    Name of the motor to move. Must be motorX, motorY or motorZ.
    position_mm  Desired position for the motor in millimeters.
    direction    Direction to move the motor. Must be 1 (forward) or 0 (backward).

Options:
    -h --help     Show this screen.
"""

from docopt import docopt
import yaml
from src.config import MotorConfig, validate_yaml_dict

from src.motor_control import MotorControl
from src.motor_control import find_serial_port

MOTORS_ID = {
    "motorX": 1,
    "motorY": 2,
    "motorZ": 3,
}

if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["<YAMLCONF>"]
    motor_name = args["<motorname>"]
    position_mm = float(args["<position_mm>"])
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
    motors_active = [key for key in yaml_dict if key.startswith("motor")]
    motors = []
    for motor_name_loop in motors_active:
        # motor_name = f"motor{chr(88 + i)}"  # 88 is ASCII for 'X'
        motor_config = MotorConfig(yaml_dict[motor_name_loop])
        motor = MotorControl(
            motors_serial,
            motor_config,
            motor_name=motor_name_loop,
            motor_id=MOTORS_ID[motor_name_loop],
        )
        motors.append(motor)

    # Move the motor to the desired position
    for motor in motors:
        if motor.motor_name == motor_name:
            # Convert the position in mm to steps
            position_steps = motor.position_to_steps(position_mm)
            motor.move_motor(direction, position_steps)
            motor.close()
