#!/usr/bin/env bash

root=$(dirname $(dirname $0))
db_name=$1
psql ${db_name} < ${root}/files/init.psql
psql ${db_name} < ${root}/files/functions.psql
