from typing import Dict, Any, Tuple
from .reader import read_bias_map
import os

def get_ref_params(yaml_dict: Dict[str, Any]) -> Tuple[list, list]:
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

def validate_yaml_dict(yaml_dict: Dict[str, Any]) -> None:
    """Validates the yaml dictionary to check if all the necessary fields are present.
    """
    assert os.path.exists(yaml_dict["config_directory"]), "La ruta especificada en config_directory no existe"
    assert os.path.exists(yaml_dict["petsys_directory"]), "La ruta especificada en petsys_directory no existe"
    assert yaml_dict["FEM"] in ["FEM128", "FEM256"], "FEM debe ser 'FEM128' o 'FEM256'"
    assert yaml_dict["FEBD"] in ["FEBD1k", "FEBD8k"], "FEBD debe ser 'FEBD1k' o 'FEBD8k'"
    assert yaml_dict["BIAS_board"] in ["BIAS_16P", "BIAS_32P", "BIAS_64P"], "BIAS_board debe ser 'BIAS_16P', 'BIAS_32P' o 'BIAS_64P'"
    assert os.path.exists(yaml_dict["bias_file"]), "El archivo bias_map.csv no existe"
    assert all(isinstance(i, float) for i in yaml_dict["ref_det_volt"]), "Todos los elementos en ref_det_volt deben ser flotantes"
    assert isinstance(yaml_dict["ref_det_volt"], list), "vth_t1 debe ser una lista"
    assert all(isinstance(i, int) for i in yaml_dict["ref_det_ths"]), "Todos los elementos en ref_det_ths deben ser flotantes"
    assert isinstance(yaml_dict["ref_det_ths"], list), "vth_t1 debe ser una lista"
    assert yaml_dict["mode"] in ["qdc", "tot"], "mode debe ser 'qdc' o 'tot'"
    assert yaml_dict["hw_trigger"] in [True, False], "hw_trigger debe ser 'True' o 'False'"
    assert yaml_dict["time"] > 0, "time debe ser mayor a 0"
    assert isinstance(yaml_dict["time"], float), "time debe ser un flotante"
    assert yaml_dict["data_type"] in ["coincidence", "singles", "group"], "data_type debe ser 'coincidence', 'singles' o 'group'"
    assert yaml_dict["data_format"] in ["binary", "txt", "root"], "data_format debe ser 'binary', 'txt' o 'root'"
    assert yaml_dict["data_compact"] in [True, False], "data_compact debe ser 'True' o 'False'"
    assert yaml_dict["fraction"] > 0 and yaml_dict["fraction"] <= 100, "fraction debe ser mayor a 0 y menor o igual a 100"
    assert isinstance(yaml_dict["fraction"], int), "fraction debe ser un int"
    assert yaml_dict["hits"] > 0 and yaml_dict["hits"] <= 64, "hits debe ser mayor a 0 y menor o igual a 64"
    assert isinstance(yaml_dict["prebreak_voltage"], float), "prebreak_voltage debe ser un flotante"
    assert isinstance(yaml_dict["break_voltage"], float), "break_voltage debe ser un flotante"
    assert isinstance(yaml_dict["over_voltage"], list), "over_voltage debe ser una lista"
    assert all(isinstance(i, float) for i in yaml_dict["over_voltage"]), "Todos los elementos en over_voltage deben ser flotantes"
    assert isinstance(yaml_dict["vth_t1"], list), "vth_t1 debe ser una lista"
    assert all(isinstance(i, int) for i in yaml_dict["vth_t1"]), "Todos los elementos en vth_t1 deben ser enteros"
    assert isinstance(yaml_dict["vth_t2"], list), "vth_t2 debe ser una lista"
    assert all(isinstance(i, int) for i in yaml_dict["vth_t2"]), "Todos los elementos en vth_t2 deben ser enteros"
    assert isinstance(yaml_dict["vth_e"], list), "vth_e debe ser una lista"
    assert all(isinstance(i, int) for i in yaml_dict["vth_e"]), "Todos los elementos en vth_e deben ser enteros"
    assert isinstance(yaml_dict["iterations"], int), "iterations debe ser un entero"