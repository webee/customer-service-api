#!/usr/bin/env bash

fin=$1
fout=$2

root=$(dirname $(dirname $0))
cd ${root}

source ${root}/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:./src

python ./src/data/transform_message_data.py <${fin} >${fout}
<${fout} sort -t $'\t' -k1,4 -k8rn,8 >${fout}.sort
