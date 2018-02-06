#!/usr/bin/env bash

env=${1:-dev}
port=${2:-5000}
NUM_WORKERS=${3:-4}
ID=${4}

PROJ_ROOT=$(dirname $0)
NAME=$(basename $PROJ_ROOT)
SRC_DIR=${PROJ_ROOT}/src
VENV_DIR=${PROJ_ROOT}/venv
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-debug}
ENV_FILE=${PROJ_ROOT}/conf/env.sh
LOG_DIR=${LOG_DIR:-${PROJ_ROOT}/logs}

#echo "Starting $NAME $env"
if [ -d ${VENV_DIR} ]; then
  source ${VENV_DIR}/bin/activate
fi
export PYTHONPATH=${SRC_DIR}:${PYTHONPATH}
export ENV=${env}
if [ -f ${ENV_FILE} ]; then
    source ${ENV_FILE}
fi

export USE_GEVENT=1

exec gunicorn main:app \
  --name ${NAME} \
  -c ${PROJ_ROOT}/deploy/gunicorn.conf.py \
  -b 0.0.0.0:${port} \
  -k gevent \
  -w ${NUM_WORKERS} \
  --access-logfile ${LOG_DIR}/access${ID}.log \
  --error-logfile ${LOG_DIR}/error${ID}.log \
  --log-level ${LOG_LEVEL}
