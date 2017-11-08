#!/usr/bin/env bash
set -e

p=${1:-dev}
db_name=cs_${p}
dropdb --if-exists ${db_name}
createdb ${db_name} -O cs_dev

./cmd.sh -e ${p} init_db
