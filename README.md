# PETsyScan

This module allows any PETsys user to acquire and process data from any PETsys systems setup.

PETsys site: [https://www.petsyselectronics.com/web/](https://www.petsyselectronics.com/web/)

## Configuration

A .yaml file is provided to select the parameters needed to acquire and process any scan/run. You can find an example configuration file in the `config/` directory.

## Installation

To install the necessary dependencies, you can use the provided `env_PETsys.yml` file with conda:

```bash
conda env create -f env_PETsys.yml
```

Usage
To run the main script, use the following command:

```bash
python Usage: main.py YAMLCONF [-m MODE]
```

Motor Firmware
The fw/ directory contains firmware for the motor control. There are separate versions for Arduino Uno R3 and I3M.

Scripts
The scripts/ directory contains additional scripts, such as go_home.py.

Source Code
The src/ directory contains the source code for the module. This includes scripts for configuration, motor control, reading data, settings, and utilities.

Test Data
The test_data/ directory contains log files and other data for testing purposes.