#!/usr/bin/env bash

fin=$1
fout=$2

root=$(dirname $(dirname $0))
cd ${root}

source ${root}/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:./src

python ./src/data/transform_message_data.py <${fin} >${fout}
<${fout} sort -t $'\t' -k1,3 -k7rn,7 >${fout}.sort
