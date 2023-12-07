import csv
import sys

def read_bias_map(bias_file: str) -> dict:
    """
    Read the bias_file.csv where all DAC_ch and ports are specified.
    INPUT: 
        bias_file - file name of the bias mapping table.
    OUTPUT:
        bias_map_dict - dictionary of a full mapping from the bias connections.
    """
    bias_map_dict = {}
    with open(bias_file) as file:
        bias_data                                   = csv.reader(file, delimiter=";")  
        febd1k_str, febd8k_str, _                   = next(bias_data, None)
        _, _, _, _, _, BIAS_64P, BIAS_16P, BIAS_32P = next(bias_data, None)
        bias_map_dict[febd1k_str]                   = {BIAS_16P:{}, BIAS_32P:{}, BIAS_64P:{}}
        bias_map_dict[febd8k_str]                   = {BIAS_16P:{}, BIAS_32P:{}, BIAS_64P:{}}
        for line in bias_data:
            port1k  = line[0]
            port8k  = int(line[2])
            slot_ID = int(line[4])
            DAC_64P = int(line[5])
            DAC_16P = int(line[6])
            DAC_32P = int(line[7])
            if port1k != 'n/a':
                port1k  = int(line[0])
                try:
                    bias_map_dict[febd1k_str][BIAS_16P][port1k].append((slot_ID, DAC_16P))
                    bias_map_dict[febd1k_str][BIAS_32P][port1k].append((slot_ID, DAC_32P)) 
                    bias_map_dict[febd1k_str][BIAS_64P][port1k].append((slot_ID, DAC_64P))
                except KeyError:
                    bias_map_dict[febd1k_str][BIAS_16P][port1k] = [(slot_ID, DAC_16P)] 
                    bias_map_dict[febd1k_str][BIAS_32P][port1k] = [(slot_ID, DAC_32P)] 
                    bias_map_dict[febd1k_str][BIAS_64P][port1k] = [(slot_ID, DAC_64P)]
            try:
                bias_map_dict[febd8k_str][BIAS_16P][port8k].append((slot_ID, DAC_16P))
                bias_map_dict[febd8k_str][BIAS_32P][port8k].append((slot_ID, DAC_32P)) 
                bias_map_dict[febd8k_str][BIAS_64P][port8k].append((slot_ID, DAC_64P))
            except KeyError:
                bias_map_dict[febd8k_str][BIAS_16P][port8k] = [(slot_ID, DAC_16P)] 
                bias_map_dict[febd8k_str][BIAS_32P][port8k] = [(slot_ID, DAC_32P)] 
                bias_map_dict[febd8k_str][BIAS_64P][port8k] = [(slot_ID, DAC_64P)]

        # remove all duplicated tupples (slot_ID, DAC_ch)
        for febd in bias_map_dict.keys():
            for bias_mez in bias_map_dict[febd].keys():
                for portID in bias_map_dict[febd][bias_mez].keys():
                    dac_chs = bias_map_dict[febd][bias_mez][portID]
                    bias_map_dict[febd][bias_mez][portID] = list(set(dac_chs))
        return bias_map_dict

if __name__ == "__main__":
    bias_file = sys.argv[1]
    read_bias_map(bias_file)
    