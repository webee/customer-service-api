#!/usr/bin/env bash

fin=$1
fout=$2

root=$(dirname $(dirname $0))
cd ${root}

source ${root}/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:./src

python ./src/data/transform_project_data.py <${fin} >${fout}
