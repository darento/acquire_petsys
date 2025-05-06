#!/usr/bin/env python3

"""Run the scan with the parameters specified in the YAMLCONF file for any
PETsys setup.
Usage: main.py YAMLCONF [-m MODE]

Arguments:
    YAMLCONF  File with all parameters to take into account in the scan.

Options:
    -h --help     Show this screen.
    -m MODE       Mode to run the scan. Can be 'acquire', 'process' or 'both' [default: both]
"""

from functools import reduce
import time
from docopt import docopt
import yaml
import pandas as pd
from typing import Dict, Any, List
import os
from itertools import product

from src.settings import BiasSettings
from src.settings import DiscSettings
from src.settings import Commands
from src.config import MotorConfig, ScanConfig, get_ref_params
from src.config import validate_yaml_dict
from src.utils import estimate_remaining_time
from src.motor_control import MotorControl
from src.motor_control import find_serial_port


def confirm_file_deletion(file_path: str) -> None:
    if os.path.exists(file_path):
        confirm = ""
        while confirm.lower() not in ["y", "n"]:
            confirm = input(
                f"The file {file_path} already exists. Do you want to delete it? (y/n): "
            )
            if confirm.lower() not in ["y", "n"]:
                print("Invalid option.")
        if confirm.lower() == "y":
            os.remove(file_path)
        elif confirm.lower() == "n":
            print(f"Appending to the end of the file with new elements.")


def process_files(petsys_commands: Commands, file_path: str, split_time: float) -> None:
    with open(file_path, "r") as f:
        next(f)  # Skip the header
        file_names = [line.split("\t")[0].strip() for line in f]
    # initialize a list to store the time each iteration takes
    iteration_times = []
    # total number of iterations
    total_iterations = len(file_names)
    # current iteration
    current_iteration = 1

    for full_out_name in file_names:
        # Record the start time of the iteration
        start_time = time.time()

        petsys_commands.process_data(full_out_name, split_time=split_time)

        # Record the end time of the iteration, and add it to the list
        end_time = time.time()
        iteration_times.append(end_time - start_time)
        estimate_remaining_time(
            iteration_times,
            total_iterations,
            current_iteration,
            string_process="process_data",
        )
        current_iteration += 1


def acquire_data_scan(
    scan_config: ScanConfig,
    time_sleep: float,
    step=-1,
) -> None:
    # TODO: curren_iteration and total_iterations are not working properly when combining motor and bias scans != single value
    # Initialize a list to store the time each iteration takes
    iteration_times = []

    # Total number of iterations
    total_iterations = reduce(
        lambda x, y: x * y, [len(sublist) for sublist in scan_config.iterables]
    )

    if step >= 0:
        total_steps = reduce(
            lambda x, y: x * y,
            [len(m.array_of_positions()) for m in scan_config.motors],
        )
        total_iterations *= total_steps

    if step >= 0:
        # current iteration
        current_iteration = step + 1
    else:
        current_iteration = 1

    iteration = -1
    # Iterate over all the possible combinations of the iterables
    for it, v, t1, t2, e in product(*scan_config.iterables):
        # Record the start time of the iteration
        start_time = time.time()

        # bias_settings.set_overvoltage(v)
        # bias_settings.write_bias_settings()
        v_bias = v + yaml_dict["break_voltage"]

        disc_settings.set_threshold(t1, "vth_t1")
        disc_settings.set_threshold(t2, "vth_t2")
        disc_settings.set_threshold(e, "vth_e")
        disc_settings.write_disc_settings()

        print(
            f"Setting bias to {v_bias}V, T1 to {t1}, T2 to {t2}, E to {e} at iteration {it}"
        )

        # Check if the motor is present
        if step >= 0:
            # Include the motor position in the file name
            full_out_name = scan_config.yaml_dict[
                "out_name"
            ] + "_pos{}_it{}_{}V_{}T1_{}T2_{}E".format(step, it, v_bias, t1, t2, e)
        else:
            # Don't include the motor position in the file name
            full_out_name = scan_config.yaml_dict[
                "out_name"
            ] + "_it{}_{}V_{}T1_{}T2_{}E".format(it, v_bias, t1, t2, e)

        file_dir = scan_config.yaml_dict["out_directory"] + full_out_name
        petsys_commands.acquire_data(full_out_name)

        print("------------------------------------------")
        time.sleep(1)

        with open(log_file, "a") as f:
            if step >= 0:
                f.write(
                    file_dir
                    + "\t"
                    + "\t".join(str(m.current_position) for m in scan_config.motors)
                    + "\n"
                )
            else:
                f.write(file_dir + "\n")

        # Record the end time of the iteration, and add it to the list
        end_time = time.time()
        iteration_times.append(end_time - start_time)

        estimate_remaining_time(
            iteration_times,
            total_iterations,
            current_iteration,
            string_process="acquire_data",
        )
        current_iteration += 1
        # sleep between iterations, when it changes
        if iteration != it:
            print(f"Sleeping for {time_sleep} seconds")
            time.sleep(time_sleep)
            iteration = it


def print_motor_position(motor: MotorControl) -> None:
    print(f"Motor '{motor.motor_name}' moved to {motor.current_position} mm/degree")


def move_motors_to_home_and_close(motors: List[MotorControl]) -> None:
    for motor in motors:
        motor.move_to_home()
        print_motor_position(motor)
        motor.close()


def close_motors(motors: List[MotorControl]) -> None:
    for motor in motors:
        motor.close()


def move_motors_and_acquire_data(
    scan_config: ScanConfig, time_sleep: float, step_ini: int = 0
) -> None:
    # Open the log file and write the header with the motor names and the milimeters
    with open(log_file, "a") as f:
        f.write(
            "file_name"
            + "\t"
            + "\t".join(str(m.motor_name) + "_mm/rev" for m in motors)
            + "\n"
        )

    # Create an array of absolute positions
    position_matrix = product(*[m.array_of_positions() for m in motors])

    # Iterate over all the possible combinations of the iterables
    for it, positions in enumerate(position_matrix):
        for motor, position in zip(scan_config.motors, positions):
            motor.move_motor_to(position)
            print_motor_position(motor)
        if it < step_ini:
            continue
        acquire_data_scan(
            scan_config,
            time_sleep,
            step=it + step_ini,
        )


if __name__ == "__main__":
    pd.set_option("display.max_rows", None)
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]
    mode = args["-m"]

    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)

    validate_yaml_dict(yaml_dict)

    dir_path = yaml_dict["config_directory"]
    current_dir = os.getcwd()

    # get the bias and discriminator settings if they exist, otherwise a empty list is returned
    bias_ref_params, disc_ref_params = get_ref_params(yaml_dict)

    # create the bias and discriminator settings objects with the reference detector parameters
    bias_settings = BiasSettings(yaml_dict, bias_ref_params)
    # bias_settings.set_fixedvoltages()
    disc_settings = DiscSettings(yaml_dict, disc_ref_params)
    disc_settings.set_fixedthresholds()

    petsys_commands = Commands(yaml_dict)

    # get the iterables
    voltages = yaml_dict["over_voltage"]
    time_T1 = yaml_dict["vth_t1"]
    time_T2 = yaml_dict["vth_t2"]
    time_E = yaml_dict["vth_e"]
    iterations = yaml_dict["iterations"]

    if iterations > 1:
        time_sleep = yaml_dict["time_between_iterations"]
    else:
        time_sleep = 0

    # Create a list of iterables to iterate over
    iterables = [range(iterations), voltages, time_T1, time_T2, time_E]

    log_file = os.path.join(yaml_dict["out_directory"], yaml_dict["out_name"] + ".log")

    # Create the output directory if it doesn't exist
    if not os.path.isdir(yaml_dict["out_directory"]):
        os.makedirs(yaml_dict["out_directory"])

    # change to the petsys directory to run the acquire_sipm_data command or process files
    petsys_directory = yaml_dict["petsys_directory"]
    os.chdir(petsys_directory)

    split_time = yaml_dict["split_time"]

    if mode == "acquire" or mode == "both":
        confirm_file_deletion(log_file)

        # Check if the motor flag is set to True
        if not yaml_dict["motor"]:
            # Open the log file and write the header
            with open(log_file, "a") as f:
                f.write("file_name" + "\n")
            # Run the acquire_data function
            no_motor_scan_conf = ScanConfig(
                bias_settings, disc_settings, yaml_dict, log_file, iterables
            )
            acquire_data_scan(no_motor_scan_conf, time_sleep)
        else:
            pos_ini = yaml_dict.get("pos_ini", 0)
            # Find the motors port
            motors_serial = find_serial_port()

            # Create a MotorControl instance for each motor
            motors = []
            for i in range(yaml_dict["num_motors"]):
                motor_name = f"motor{chr(88 + i)}"  # 88 is ASCII for 'X'
                motor_config = MotorConfig(yaml_dict[motor_name])
                motor = MotorControl(
                    motors_serial, motor_config, motor_name=motor_name, motor_id=i + 1
                )
                motors.append(motor)
            # for motor in motors:
            #     motor.find_home()
            motor_scan_conf = ScanConfig(
                bias_settings, disc_settings, yaml_dict, log_file, iterables, motors
            )
            move_motors_and_acquire_data(motor_scan_conf, time_sleep, pos_ini)
            close_motors(motors)

        if mode == "both":
            process_files(petsys_commands, log_file, split_time)
    elif mode == "process":
        process_files(petsys_commands, log_file, split_time)
    else:
        print("Mode [-m] not valid. You can choose 'acquire', 'process' o 'both'")
    # change back to the original directory
    os.chdir(current_dir)
