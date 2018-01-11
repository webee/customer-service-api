#!/usr/bin/env bash

env=${1:-dev}
port=${2:-5000}
NUM_WORKERS=${3:-4}

PROJ_ROOT=$(dirname $0)
NAME=$(basename $PROJ_ROOT)
SRC_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/venv
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-debug}
ENV_FILE=${PROJ_ROOT}/conf/env.sh

#echo "Starting $NAME $env"
if [ -d ${VENV_DIR} ]; then
  source ${VENV_DIR}/bin/activate
fi
export PYTHONPATH=${SRC_DIR}:${PYTHONPATH}
export ENV=${env}
if [ -f ${ENV_FILE} ]; then
    source ${ENV_FILE}
fi

exec gunicorn main:app \
  --name ${NAME} \
  -c ${PROJ_ROOT}/deploy/gunicorn.conf.py \
  -b 0.0.0.0:${port} \
  -k gevent \
  -w ${NUM_WORKERS} \
  --access-logfile ${PROJ_ROOT}/logs/access.log \
  --error-logfile ${PROJ_ROOT}/logs/error.log \
  --log-level ${LOG_LEVEL}
