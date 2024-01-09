#!/bin/bash
CONDA_ENV_NAME=env_PETsys
YML_FILENAME=${CONDA_ENV_NAME}.yml
source /home/metamaterials/miniconda/bin/activate ${CONDA_ENV_NAME}
python setup.py develop
echo "Environment activated."
echo "To deactivate type: conda deactivate"