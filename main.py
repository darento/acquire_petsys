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

import time
from docopt import docopt
import yaml
import pandas as pd
from typing import Dict, Any, List
import os
import sys

from src.settings      import BiasSettings
from src.settings      import DiscSettings
from src.settings      import Commands
from src.config        import get_ref_params
from src.config        import validate_yaml_dict
from src.utils         import estimate_remaining_time
from src.motor_control import MotorControl
from src.motor_control import serial_ports

def confirm_file_deletion(file_path: str) -> None:
    if os.path.exists(file_path):
        confirm = ''
        while confirm.lower() not in ['y', 'n']:
            confirm = input(f"The file {file_path} already exists. Do you want to delete it? (y/n): ")
            if confirm.lower() not in ['y', 'n']:
                print("Invalid option.")
        if confirm.lower() == 'y':
            os.remove(file_path)
        elif confirm.lower() == 'n':
            print(f"Appending to the end of the file with new elements.")

def process_files(petsys_commands: Commands, file_path: str)-> None:
    with open(file_path, 'r') as f:
        file_names = f.read().splitlines()
    # initialize a list to store the time each iteration takes
    iteration_times = []
    # total number of iterations
    total_iterations = len(file_names)
    # current iteration
    current_iteration = 0

    for full_out_name in file_names:
        # Record the start time of the iteration
        start_time = time.time()

        petsys_commands.process_data(full_out_name)
        
        # Record the end time of the iteration, and add it to the list
        end_time = time.time()
        iteration_times.append(end_time - start_time)
        estimate_remaining_time(iteration_times, total_iterations, current_iteration, string_process = "process_data")
        current_iteration += 1

def acquire_data(bias_settings: BiasSettings, 
                 disc_settings: DiscSettings,
                 yaml_dict: Dict[str, Any], 
                 all_files_name: str, 
                 iterations: int, 
                 voltages: list, 
                 time_T1:list, 
                 time_T2:list, 
                 time_E:list)-> None:
    # Initialize a list to store the time each iteration takes
    iteration_times = []

    # Total number of iterations
    total_iterations = len(time_E) * len(time_T2) * len(time_T1) * len(voltages) * iterations

    # Current iteration
    current_iteration = 0

    for it in range(iterations):
        for v in voltages:
            bias_settings.set_overvoltage(v)
            bias_settings.write_bias_settings()
            v_bias = v + yaml_dict["break_voltage"]
            for t1 in time_T1:
                disc_settings.set_threshold(t1, "vth_t1")
                for t2 in time_T2:
                    disc_settings.set_threshold(t2, "vth_t2")
                    for e in time_E:
                        # Record the start time of the iteration
                        start_time = time.time()

                        print(f"Setting bias to {v_bias}V, T1 to {t1}, T2 to {t2}, E to {e} at iteration {it}")
                        disc_settings.set_threshold(e, "vth_e")
                        disc_settings.write_disc_settings()
                        full_out_name = yaml_dict["out_name"] + "_it{}_{}OV_{}T1_{}T2_{}E".format(it, v_bias, t1, t2, e)
                        file_dir = yaml_dict["out_directory"] + full_out_name
                        petsys_commands.acquire_data(full_out_name)
                        print("------------------------------------------")
                        time.sleep(1)
                        with open(all_files_name, 'a') as f:
                            f.write(file_dir + '\n')

                        # Record the end time of the iteration, and add it to the list
                        end_time = time.time()
                        iteration_times.append(end_time - start_time)

                        estimate_remaining_time(iteration_times, total_iterations, current_iteration, string_process = "acquire_data")

                        current_iteration += 1


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]
    mode = args["-m"]
    
    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)                

    validate_yaml_dict(yaml_dict)
    
    dir_path      = yaml_dict["config_directory"]
    current_dir = os.getcwd()
    

    # get the bias and discriminator settings if they exist, otherwise a empty list is returned
    bias_ref_params, disc_ref_params = get_ref_params(yaml_dict)
    
    # create the bias and discriminator settings objects with the reference detector parameters
    bias_settings = BiasSettings(yaml_dict, bias_ref_params)
    bias_settings.set_fixedvoltages()
    disc_settings = DiscSettings(yaml_dict, disc_ref_params)
    disc_settings.set_fixedthresholds()

    petsys_commands = Commands(yaml_dict)
    voltages = yaml_dict["over_voltage"]
    time_T1 = yaml_dict["vth_t1"]
    time_T2 = yaml_dict["vth_t2"]
    time_E = yaml_dict["vth_e"]
    iterations = yaml_dict["iterations"]
    all_files_name = os.path.join(yaml_dict["out_directory"], yaml_dict["out_name"] + '.txt')

    # change to the petsys directory to run the acquire_sipm_data command or process files
    petsys_directory = yaml_dict["petsys_directory"]
    os.chdir(petsys_directory)

    if mode == "acquire" or mode == "both":
        confirm_file_deletion(all_files_name) 

        # Check if the motor flag is set to True
        if not yaml_dict['motor']:
            # Run the acquire_data function
            acquire_data(bias_settings, disc_settings, yaml_dict, all_files_name, iterations, voltages, time_T1, time_T2, time_E)
        else:
            # Find the motor port
            motor_port = serial_ports()

            if motor_port is None:
                print("No motor port found")
                sys.exit(1)

            # Create a MotorControl instance for each motor
            motors = []
            for i in range(yaml_dict['num_motors']):
                motor_name = f"motor{chr(88 + i)}"  # 88 is ASCII for 'X'
                motor_config = yaml_dict[motor_name]
                motor = MotorControl(motor_port, motor_config['relation'], 
                                    motor_config['microstep'], motor_config['start'], 
                                    motor_config['end'], motor_config['step_size'])
                motors.append(motor)
            
            # Move each motor to start
            for motor in motors:
                motor.move_to_start()     
            # Loop to move each motor step by step and acquire data
            while any(motor.current_position_mm < motor.motor_end for motor in motors):
                for motor in motors:
                    # Move motor to the next step if it hasn't reached the end
                    if motor.current_position_mm < motor.motor_end:
                        motor.next_step()
                        print(f"Motor moved to {motor.current_position_mm}mm")

                        # Run the acquire_data function
                        acquire_data(bias_settings, disc_settings, yaml_dict, all_files_name, iterations, voltages, time_T1, time_T2, time_E)

                        # Add a delay or wait for user input or signal from other script as needed
                        time.sleep(1)  
                        
            # Move each motor to home and close the motor port when done
            for motor in motors:
                motor.move_to_home()
                print(f"Motor moved to {motor.current_position_mm}mm")
                motor.close()                
        if mode == "both":
            process_files(petsys_commands, all_files_name)
    elif mode == "process":
        process_files(petsys_commands, all_files_name)
    else:
        print("Mode [-m] not valid. You can choose 'acquire', 'process' o 'both'")
    # change back to the original directory
    os.chdir(current_dir)