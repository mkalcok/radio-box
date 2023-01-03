#!/bin/bash

source "$SNAP"/config-handler
PORT=$(get_port)
ADDRESS=$(get_address)
WORKERS=$(get_workers)

"$SNAP"/usr/bin/gunicorn "radio_box.rest_api:create_app()" --workers "$WORKERS" --bind "$ADDRESS:$PORT"