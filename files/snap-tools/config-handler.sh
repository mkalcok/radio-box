#!/bin/bash

DEFAULT_PORT="80"
DEFAULT_ADDRESS="0.0.0.0"
DEFAULT_WORKERS=4

get_address()
{
  local address
  address="$(snapctl get address)"

  if [ -z "$address" ]; then
    address="$DEFAULT_ADDRESS"
    set_address $address
  fi
    echo "$address"
}

set_address()
{
  snapctl set address="$1"
}

get_port()
{
  local port
  port="$(snapctl get port)"
  if [ -z "$port" ]; then
    port="$DEFAULT_PORT"
    set_port $port
  fi
    echo "$port"
}

set_port()
{
  snapctl set port="$1"
}

get_workers()
{
  local workers
  workers="$(snapctl get workers)"
  if [ -z "$workers" ]; then
    workers="$DEFAULT_WORKERS"
    set_workers $workers
  fi
    echo "$workers"
}

set_workers()
{
  snapctl set workers="$1"
}
