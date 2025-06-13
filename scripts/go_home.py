#!/usr/bin/env python3

"""Move the motor to the home position. Reverse the direction of the motor if it is not moving in the right direction.
Usage: go_home.py YAMLCONF

Arguments:
    YAMLCONF  File with all parameters to take into account in the scan.

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
    yaml_conf = args["YAMLCONF"]

    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)

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
    for motor in motors:
        motor.find_home()
