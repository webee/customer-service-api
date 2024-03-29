#!/usr/bin/env bash
set -e
set -x

p=${1:-dev}
u=${2:-$(whoami)}

db_name=cs_${p}
sudo -u ${u} dropdb --if-exists ${db_name}
sudo -u ${u} createdb ${db_name} -O cs_dev
sudo -u ${u} ./scripts/prepare_db.sh ${db_name}

./cmd.sh -e ${p} init_db
