#!/usr/bin/env python3

"""Generates detector spectrum and CTR if needed for 
FUTURA detector setup
Usage: main.py YAMLCONF

Arguments:
    YAMLCONF  File with all parameters to take into account in the scan.

"""
from docopt import docopt
import yaml

from src.util import set_fixedvoltages
from src.util import set_Ethreshold
from src.util import write_disc_settings
from src.util import set_T2threshold
from src.util import set_overvoltage
from src.util import write_bias_settings
from src.util import set_T1threshold
from src.util import acquire_command
from src.util import process_command

if __name__ == "__main__":
    args = docopt(__doc__)
    yaml_conf = args["YAMLCONF"]


    with open(yaml_conf) as yaml_reader:
        yaml_dict = yaml.safe_load(yaml_reader)

    print(yaml_dict)
    exit(0)

    dictionary = yaml.safe_load(fd)
    print("----------")
    bias_df = set_fixedvoltages(dictionary)
    voltages = dictionary["over_voltage"]
    T1_th = dictionary["T1_th"][0]
    T2_th = dictionary["T2_th"][0]
    E_th = dictionary["E_th"][0]
    time_T1 = dictionary["T1_time_th"]
    time_T2 = dictionary["T2_time_th"]
    time_E = dictionary["E_time_th"]
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