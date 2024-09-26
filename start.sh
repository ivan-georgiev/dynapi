#!/bin/bash

env | grep DYNAPP
ERROR_FILE=${DYNAPP_ERROR_FILE_PATH:-/app/error_file}

[[ -z "$DYNAPP_PORT" ]] && DYNAPP_PORT=8080

[[ -f "/var/config/.env" ]] && echo "INFO: .env file found" && . /var/config/.env

[[ ! -z "$DYNAPP_AUTODESTROY_TIME" ]] && echo "WARNING: DYNAPP_AUTODESTROY_TIME is set to $DYNAPP_AUTODESTROY_TIME" &&  (sleep $DYNAPP_AUTODESTROY_TIME && touch $ERROR_FILE) &

if [ "$DYNAPP_NOSIGNALS" == "true" ]; then
    echo "INFO: DYNAPP_NOSIGNALS is set, Ctrl+C will not work."
    uvicorn main:app --host 0.0.0.0 --port $DYNAPP_PORT
else
    exec uvicorn main:app --host 0.0.0.0 --port $DYNAPP_PORT
fi