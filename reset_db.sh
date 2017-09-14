#!/usr/bin/env bash
set -e

dropdb custom_service
createdb custom_service -O cs

./cmd.sh init_db
