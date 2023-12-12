import os
import pandas as pd
import shutil



class BiasSettings:
    def __init__(self, dictionary, bias_ref_params):
        self.dictionary = dictionary
        self.bias_ref_params = set(bias_ref_params)
        self.bias_settings_path = dictionary["config_directory"]
        self.bias_settings_file_name = "bias_settings.tsv"
        self.bias_df = pd.read_csv(self.bias_settings_path + self.bias_settings_file_name, sep = '\t')

    def set_fixedvoltages(self):
        self.bias_df["Pre-breakdown"] = self.dictionary["prebreak_voltage"]
        self.bias_df["Breakdown"] = self.dictionary["break_voltage"]
        if self.bias_ref_params:
            ref_det_volt = self.dictionary["ref_det_volt"]
            for slot, channel in self.bias_ref_params:
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Pre-breakdown'] = ref_det_volt[0]
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Breakdown'] = ref_det_volt[1]
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Overvoltage'] = ref_det_volt[2]

    def set_overvoltage(self, voltage):
        self.bias_df.loc[~self.bias_df[['slotID', 'channelID']].apply(tuple, axis=1).isin(self.bias_ref_params), 'Overvoltage'] = voltage

    def write_bias_settings(self):
        new_bias_settings_path = self.dictionary["config_directory"]
        new_bias_settings_file_name = "bias_settings.tsv"
        full_path = new_bias_settings_path + new_bias_settings_file_name

        # Create a backup of the original file
        shutil.copy(full_path, full_path.replace(".tsv", "_backup.tsv"))

        # Write the new bias settings
        self.bias_df.to_csv(full_path, index = False, sep = '\t')


class DiscSettings:
    
    def __init__(self, dictionary, disc_ref_params):
        self.dictionary = dictionary
        self.disc_ref_params = set(disc_ref_params)
        self.disc_settings_path = dictionary["config_directory"]
        self.disc_settings_file_name = "disc_settings.tsv"
        self.disc_df = pd.read_csv(self.disc_settings_path + self.disc_settings_file_name, sep = '\t')
        
    def set_fixedthresholds(self):
        self.disc_df["vth_t1"] = self.dictionary["vth_t1"][0]
        self.disc_df["vth_t2"] = self.dictionary["vth_t2"][0]
        self.disc_df["vth_e"] = self.dictionary["vth_e"][0]
        if self.disc_ref_params:
            ref_det_th = self.dictionary["ref_det_ths"]
            for chipID in self.disc_ref_params:
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_t1'] = ref_det_th[0]
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_t2'] = ref_det_th[1]
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_e'] = ref_det_th[2]

    def set_threshold(self, threshold, key):
        self.disc_df.loc[~self.disc_df[['chipID']].isin(self.disc_ref_params).any(1), key] = threshold
    
    def write_disc_settings(self):
        new_disc_settings_path = self.dictionary["config_directory"]
        new_disc_settings_file_name = "disc_settings.tsv"
        full_path = new_disc_settings_path + new_disc_settings_file_name

        # Create a backup of the original file
        shutil.copy(full_path, full_path.replace(".tsv", "_backup.tsv"))

        # Write the new discriminator settings
        self.disc_df.to_csv(full_path, index = False, sep = '\t')


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