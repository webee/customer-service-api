#!/usr/bin/env bash

dropdb custom_service
createdb custom_service -O cs

./cmd.sh init_db
