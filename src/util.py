import os
import pandas as pd

def set_fixedvoltages(dictionary):
    bias_settings_path = dictionary["config_directory"]
    bias_settings_file_name = "bias_settings.tsv"
    bias_df = pd.read_csv(bias_settings_path + bias_settings_file_name, sep = '\t')
    bias_df["Pre-breakdown"] = dictionary["prebreak_voltage"]
    bias_df["Breakdown"] = dictionary["break_voltage"]

    #rename bias_settings.tsv in case something went wrong
    bias_settings_file_name_backup = "bias_settings_backup.tsv"
    os.rename(bias_settings_path + bias_settings_file_name, bias_settings_path + bias_settings_file_name_backup)
    return bias_df

def set_overvoltage(bias_df, voltage):
    bias_df["Overvoltage"] = voltage
    return bias_df

def write_bias_settings(bias_df, dictionary):
    new_bias_settings_path = dictionary["config_directory"]
    new_bias_settings_file_name = "bias_settings.tsv"
    bias_df.to_csv(new_bias_settings_path + new_bias_settings_file_name, index = False, sep = '\t')

def set_T1threshold(dictionary, T1_th, T1_time):
    disc_settings_path = dictionary["config_directory"]
    disc_settings_file_name = "disc_settings.tsv"
    disc_df = pd.read_csv(disc_settings_path + disc_settings_file_name, sep = '\t')
    disc_df["vth_t1"] = T1_th

    chip_ID = dictionary["chip_ID"]
    time_ID = dictionary["time_channels"]
    time_T1 = dictionary["T1_time_th"][0]

    for chip in chip_ID:
        for tID in time_ID:
            tID_petsys = tID - 64 * chip
            disc_df.loc[(disc_df['chipID'] == chip) & (disc_df['channelID'] ==  tID_petsys), 'vth_t1'] = T1_time

    #rename bias_settings.tsv in case something went wrong
    disc_settings_file_name_backup = "disc_settings_backup.tsv"
    os.rename(disc_settings_path + disc_settings_file_name, disc_settings_path + disc_settings_file_name_backup)
    return disc_df

def set_T2threshold(dictionary, T2_th, T2_time):
    disc_settings_path = dictionary["config_directory"]
    disc_settings_file_name = "disc_settings.tsv"
    disc_df = pd.read_csv(disc_settings_path + disc_settings_file_name, sep = '\t')
    disc_df["vth_t2"] = T2_th

    chip_ID = dictionary["chip_ID"]
    time_ID = dictionary["time_channels"]

    for chip in chip_ID:
        for tID in time_ID:
            tID_petsys = tID - 64 * chip
            disc_df.loc[(disc_df['chipID'] == chip) & (disc_df['channelID'] ==  tID_petsys), 'vth_t2'] = T2_time

    #rename bias_settings.tsv in case something went wrong
    disc_settings_file_name_backup = "disc_settings_backup.tsv"
    os.rename(disc_settings_path + disc_settings_file_name, disc_settings_path + disc_settings_file_name_backup)
    return disc_df

def set_Ethreshold(dictionary, E_th, E_time):
    disc_settings_path = dictionary["config_directory"]
    disc_settings_file_name = "disc_settings.tsv"
    disc_df = pd.read_csv(disc_settings_path + disc_settings_file_name, sep = '\t')
    disc_df["vth_e"] = E_th

    chip_ID = dictionary["chip_ID"]
    time_ID = dictionary["time_channels"]

    for chip in chip_ID:
        for tID in time_ID:
            tID_petsys = tID - 64 * chip
            disc_df.loc[(disc_df['chipID'] == chip) & (disc_df['channelID'] ==  tID_petsys), 'vth_e'] = E_time

    #rename bias_settings.tsv in case something went wrong
    disc_settings_file_name_backup = "disc_settings_backup.tsv"
    os.rename(disc_settings_path + disc_settings_file_name, disc_settings_path + disc_settings_file_name_backup)
    return disc_df

def write_disc_settings(disc_df, dictionary):
    new_disc_settings_path = dictionary["config_directory"]
    new_disc_settings_file_name = "disc_settings.tsv"
    disc_df.to_csv(new_disc_settings_path + new_disc_settings_file_name, index = False, sep = '\t')

def acquire_command(dictionary, full_out_name):
    if not os.path.isdir(dictionary["out_directory"]):
        os.makedirs(dictionary["out_directory"])
    if dictionary["hw_trigger"]:
        hw_trigger = "--enable-hw-trigger"
    else:
        hw_trigger = ""
    os.system("./acquire_sipm_data --config {} --mode {} --time {} -o {} {}".format(dictionary["config_directory"] + "config.ini",
    dictionary["mode"], dictionary["time"], dictionary["out_directory"] + full_out_name, hw_trigger))

def process_command(dictionary, full_out_name):
    if dictionary["data_type"] == "coincidence":
        sufix = "_coinc"
        process_command = "./convert_raw_to_coincidence"
    elif dictionary["data_type"] == "single":
        sufix = "_single"
        process_command = "./convert_raw_to_single"
    elif dictionary["data_type"] == "group":
        sufix = "_group"
        process_command = "./convert_raw_to_group"
    if dictionary["data_format"] == "txt":
        output_format = ""
        #sufix_2 = ".dat"
    elif dictionary["data_format"] == "binary":
        output_format = "--writeBinary"
        #sufix_2 = ".ldat"
    elif dictionary["data_format"] == "root":
        output_format = "--writeRoot"
        #sufix_2 = ".root"
    process_out_name = full_out_name + sufix
    print(process_out_name)
    os.system("{} --config {} -i {} -o {} --writeMultipleHits {} {}".format(process_command, dictionary["config_directory"] + "config.ini",
    dictionary["out_directory"] + full_out_name, dictionary["out_directory"] + process_out_name, dictionary["hits"], output_format))