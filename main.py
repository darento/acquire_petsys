#!/usr/bin/env python3

"""Generates detector spectrum and CTR if needed for 
FUTURA detector setup
Usage: main.py YAMLCONF

Arguments:
    YAMLCONF  File with all parameters to take into account in the scan.

"""
import time
from docopt import docopt
import yaml
import pandas as pd
from typing import Dict, Any

from src.reader     import read_bias_map
from src.settings   import BiasSettings
from src.settings   import DiscSettings
from src.settings   import Commands
from src.config     import get_ref_params
from src.config     import validate_yaml_dict




if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]


    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)

    validate_yaml_dict(yaml_dict)
    
    dir_path      = yaml_dict["config_directory"]

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
    for it in range(iterations):
        for v in voltages:
            bias_df = bias_settings.bias_df.copy()
            disc_df = disc_settings.disc_df.copy()
            bias_df = bias_settings.set_overvoltage(v)
            bias_settings.write_bias_settings()
            v_bias = v + yaml_dict["break_voltage"]
            for t1 in time_T1:
                disc_df = disc_settings.set_threshold( t1, "vth_t1")
                for t2 in time_T2:
                    disc_df = disc_settings.set_threshold(t2, "vth_t2")
                    for e in time_E:
                        disc_df = disc_settings.set_threshold(e, "vth_e")
                        disc_settings.write_disc_settings()
                        full_out_name = yaml_dict["out_name"] + "_it{}_{}OV_{}T1_{}T2_{}E".format(it, v_bias, t1, t2, e)
                        petsys_commands.acquire_data(full_out_name)
                        petsys_commands.process_data(full_out_name)
                        print(f"Setting bias to {v_bias}V, T1 to {t1}, T2 to {t2}, E to {e} at iteration {it}")
                        print("------------------------------------------")
                        time.sleep(3)