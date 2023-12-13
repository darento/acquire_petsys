import os
import pandas as pd
import shutil
from typing import Dict, Any



class BiasSettings:
    def __init__(self, dictionary: Dict[str, Any], 
                 bias_ref_params: list):
        self.dictionary = dictionary
        self.bias_ref_params = set(bias_ref_params)
        self.bias_settings_path = dictionary["config_directory"]
        self.bias_settings_file_name = "bias_settings.tsv"
        self.bias_df = pd.read_csv(self.bias_settings_path + self.bias_settings_file_name, sep = '\t')

    def set_fixedvoltages(self) -> None:
        self.bias_df["Pre-breakdown"] = self.dictionary["prebreak_voltage"]
        self.bias_df["Breakdown"] = self.dictionary["break_voltage"]
        if self.bias_ref_params:
            ref_det_volt = self.dictionary["ref_det_volt"]
            for slot, channel in self.bias_ref_params:
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Pre-breakdown'] = ref_det_volt[0]
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Breakdown'] = ref_det_volt[1]
                self.bias_df.loc[(self.bias_df['slotID'] == slot) & (self.bias_df['channelID'] == channel), 'Overvoltage'] = ref_det_volt[2]

    def set_overvoltage(self, 
                        voltage: float
                        ) -> None:
        self.bias_df.loc[~self.bias_df[['slotID', 'channelID']].apply(tuple, axis=1).isin(self.bias_ref_params), 'Overvoltage'] = voltage

    def write_bias_settings(self) -> None:
        new_bias_settings_path = self.dictionary["config_directory"]
        new_bias_settings_file_name = "bias_settings.tsv"
        full_path = new_bias_settings_path + new_bias_settings_file_name

        # Create a backup of the original file
        shutil.copy(full_path, full_path.replace(".tsv", "_backup.tsv"))

        # Write the new bias settings
        self.bias_df.to_csv(full_path, index = False, sep = '\t')


class DiscSettings:
    
    def __init__(self, dictionary: Dict[str, Any], 
                 disc_ref_params: list):
        self.dictionary = dictionary
        self.disc_ref_params = set(disc_ref_params)
        self.disc_settings_path = dictionary["config_directory"]
        self.disc_settings_file_name = "disc_settings.tsv"
        self.disc_df = pd.read_csv(self.disc_settings_path + self.disc_settings_file_name, sep = '\t')
        
    def set_fixedthresholds(self) -> None:
        self.disc_df["vth_t1"] = self.dictionary["vth_t1"][0]
        self.disc_df["vth_t2"] = self.dictionary["vth_t2"][0]
        self.disc_df["vth_e"] = self.dictionary["vth_e"][0]
        if self.disc_ref_params:
            ref_det_th = self.dictionary["ref_det_ths"]
            for chipID in self.disc_ref_params:
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_t1'] = ref_det_th[0]
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_t2'] = ref_det_th[1]
                self.disc_df.loc[(self.disc_df['chipID'] == chipID), 'vth_e'] = ref_det_th[2]

    def set_threshold(self, threshold: int, 
                     key: str) -> None:
        self.disc_df.loc[~self.disc_df[['chipID']].isin(self.disc_ref_params).any(1), key] = threshold
    
    def write_disc_settings(self) -> None:
        new_disc_settings_path = self.dictionary["config_directory"]
        new_disc_settings_file_name = "disc_settings.tsv"
        full_path = new_disc_settings_path + new_disc_settings_file_name

        # Create a backup of the original file
        shutil.copy(full_path, full_path.replace(".tsv", "_backup.tsv"))

        # Write the new discriminator settings
        self.disc_df.to_csv(full_path, index = False, sep = '\t')


class Commands:
    def __init__(self, dictionary: Dict[str, Any]):
        self.dictionary = dictionary

    def acquire_data(self, full_out_name: str) -> None:
        if not os.path.isdir(self.dictionary["out_directory"]):
            os.makedirs(self.dictionary["out_directory"])
        hw_trigger = "--enable-hw-trigger" if self.dictionary["hw_trigger"] else ""

        command = (
            f"./acquire_sipm_data --config {self.dictionary['config_directory']}config.ini "
            f"--mode {self.dictionary['mode']} --time {self.dictionary['time']} "
            f"-o {self.dictionary['out_directory']}{full_out_name} {hw_trigger}"
        )

        print(command + "\n")
        #os.system(command)

    def process_data(self, full_out_name: str) -> None:
        data_type_mapping = {
            "coincidence": ("_coinc", "./convert_raw_to_coincidence"),
            "single": ("_single", "./convert_raw_to_single"),
            "group": ("_group", "./convert_raw_to_group")
        }
        data_format_mapping = {
            "txt": "",
            "binary": "--writeBinary",
            "root": "--writeRoot"
        }
        sufix, process_command = data_type_mapping[self.dictionary["data_type"]]
        output_format = data_format_mapping[self.dictionary["data_format"]]
        process_out_name = full_out_name + sufix

        command = (
            f"{process_command} --config {self.dictionary['config_directory']}config.ini "
            f"-i {self.dictionary['out_directory']}{full_out_name} "
            f"-o {self.dictionary['out_directory']}{process_out_name} "
            f"--writeMultipleHits {self.dictionary['hits']} {output_format}"
        )
        
        print(command + "\n")
        #os.system(command)
    

