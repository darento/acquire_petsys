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
from typing import Dict, Any
import os

from src.settings   import BiasSettings
from src.settings   import DiscSettings
from src.settings   import Commands
from src.config     import get_ref_params
from src.config     import validate_yaml_dict

def confirm_file_deletion(file_path: str) -> None:
    if os.path.exists(file_path):
        confirm = ''
        while confirm.lower() not in ['s', 'n']:
            confirm = input(f"El archivo {file_path} ya existe. ¿Desea eliminarlo? (s/n): ")
            if confirm.lower() not in ['s', 'n']:
                print("Opción no válida.")
        if confirm.lower() == 's':
            os.remove(file_path)
        elif confirm.lower() == 'n':
            print(f"Se hará un append al final del fichero con los nuevos elementos.")

def process_files(petsys_commands: Commands, file_path: str)-> None:
    with open(file_path, 'r') as f:
        file_names = f.read().splitlines()
    for full_out_name in file_names:
        petsys_commands.process_data(full_out_name)

def acquire_data(bias_settings: BiasSettings, 
                 disc_settings: DiscSettings,
                 yaml_dict: Dict[str, Any], 
                 all_files_name: str, 
                 iterations: int, 
                 voltages: list, 
                 time_T1:list, 
                 time_T2:list, 
                 time_E:list)-> None:
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
                        print(f"Setting bias to {v_bias}V, T1 to {t1}, T2 to {t2}, E to {e} at iteration {it}")
                        disc_settings.set_threshold(e, "vth_e")
                        disc_settings.write_disc_settings()
                        full_out_name = yaml_dict["out_name"] + "_it{}_{}OV_{}T1_{}T2_{}E".format(it, v_bias, t1, t2, e)
                        file_dir = yaml_dict["out_directory"] + full_out_name
                        petsys_commands.acquire_data(full_out_name)
                        print(file_dir)
                        print("------------------------------------------")
                        time.sleep(1)
                        with open(all_files_name, 'a') as f:
                            f.write(file_dir + '\n')


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
        acquire_data(bias_settings, disc_settings, yaml_dict, all_files_name, iterations, voltages, time_T1, time_T2, time_E)        
        if mode == "both":
            process_files(petsys_commands, all_files_name)
    elif mode == "process":
        process_files(petsys_commands, all_files_name)
    else:
        print("Modo [-m] no válido. Puede ser 'acquire', 'process' o 'both'")
    # change back to the original directory
    os.chdir(current_dir)