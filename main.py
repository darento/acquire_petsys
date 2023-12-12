#!/usr/bin/env python3

"""Generates detector spectrum and CTR if needed for 
FUTURA detector setup
Usage: main.py YAMLCONF

Arguments:
    YAMLCONF  File with all parameters to take into account in the scan.

"""
from docopt import docopt
import yaml
import pandas as pd

from src.reader import read_bias_map
from src.util   import BiasSettings
from src.util   import DiscSettings
from src.util   import acquire_command
from src.util   import process_command


def get_ref_params(yaml_dict):
    bias_map_dict = read_bias_map(yaml_dict["bias_file"])
    FEM           = yaml_dict["FEM"]
    FEBD          = yaml_dict["FEBD"]
    BIAS_board    = yaml_dict["BIAS_board"]
    #ref detector if there is some
    ref_det_febd = yaml_dict["ref_det_febd"]
    if ref_det_febd != -1:
        #bias_params: list of tuples consisting of [(slotID, channelID)]
        bias_params = bias_map_dict[FEBD][BIAS_board][ref_det_febd]   
        num_ASICs = 2 if FEM == "FEM128" else 4
        disc_params = [ref_det_febd * num_ASICs, ref_det_febd * num_ASICs + 1]
        return bias_params, disc_params
    else:
        return [], []


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]


    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)
    dir_path      = yaml_dict["config_directory"]

    # get the bias and discriminator settings if they exist, otherwise a empty list is returned
    bias_ref_params, disc_ref_params = get_ref_params(yaml_dict)
    
    # create the bias and discriminator settings objects with the reference detector parameters
    bias_settings = BiasSettings(yaml_dict, bias_ref_params)
    bias_settings.set_fixedvoltages()
    disc_settings = DiscSettings(yaml_dict, disc_ref_params)
    disc_settings.set_fixedthresholds()

    voltages = yaml_dict["voltages"]
    for v in voltages:
        for e in time_E:
            disc_df = set_Ethreshold(dictionary, E_th, e)
            write_disc_settings(disc_df, dictionary)
            for t2 in time_T2:
                disc_df = set_T2threshold(dictionary, T2_th, t2)
                write_disc_settings(disc_df, dictionary)
                for t1 in time_T1:
                    print("OV, T1, T2, E: {}, {}, {}, {}".format(v, t1, t2, e))
                    bias_df = set_overvoltage(bias_df, v)
                    write_bias_settings(bias_df, dictionary)
                    disc_df = set_T1threshold(dictionary, T1_th, t1)
                    write_disc_settings(disc_df, dictionary)
                    full_out_name = dictionary["out_name"] + "_{}OV_{}T1_{}T2_{}E".format(v, t1, t2, e)
                    acquire_command(dictionary, full_out_name)
                    process_command(dictionary, full_out_name)