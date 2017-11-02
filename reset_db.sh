#!/usr/bin/env bash
set -e

dropdb cs_dev
createdb cs_dev -O cs

./cmd.sh init_db
