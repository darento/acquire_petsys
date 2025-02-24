# ACQUIRE_PETSYS

This module allows any PETsys user to acquire and process data from any PETsys systems setup.

PETsys site: [https://www.petsyselectronics.com/web/](https://www.petsyselectronics.com/web/)

## Configuration

A .yaml file is provided to select the parameters needed to acquire and process any `scan/run`. You can find an example configuration file in the `config/` directory.

## Installation

### Windows

To install the necessary dependencies, you can use the provided `acquire_petsys.yml` file with conda:

```bash
conda env create -f acquire_petsys.yml
```
### Linux

```bash
source make_condaENV.sh 
```
or again
```bash
conda env create -f acquire_petsys.yml
```

## Usage

First of all, you need to activate the conda enviorment:

```bash
source /home/user/miniconda/bin/activate acquire_petsys
```

Then, to run the script to perform the PETsys scan, use the following command:

```bash
python Usage: main.py YAMLCONF [-m MODE]
```
Anything you want to change on your setup, you should change it in the `.yaml` file you are using to run the scan. 

## Motor Firmware
The fw/ directory contains firmware for the motor control. There are separate versions for Arduino Uno R3 and Arduino I3M.

## Scripts
The `scripts/` directory contains additional scripts, such as `go_home.py`.

## Source Code
The `src/` directory contains the source code for the module. This includes scripts for configuration, motor control, reading data, settings, and utilities.

## Test Data
The `test_data/` directory contains log files and other data for testing purposes.
