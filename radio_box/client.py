import argparse
from pathlib import Path

import yaml

from radio_box.common import (
    create_pipe,
    make_message_play,
    make_message_quit,
    make_message_stop,
    send_message,
)

PLAY = "play"
STOP = "stop"
QUIT = "quit"


def parse_args() -> argparse.Namespace:
    description = "Radio-box CLI client"
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(title="commands", dest="subparser_command")

    parser.add_argument(
        "-c", "--config", default="/etc/radio-box/conf.yaml", help="Config file path"
    )
    parser.add_argument(
        "-s",
        "--socket",
        help="Communication socket with radio-box service.",
        required=False,
    )

    play_parser = subparsers.add_parser(PLAY)
    play_parser.add_argument("station", help="Station name to play")

    subparsers.add_parser(STOP)
    subparsers.add_parser(QUIT)

    return parser.parse_args()


def play(socket_path: Path, station: str) -> None:
    message = make_message_play(station)
    send_message(socket_path, message)


def stop(socket_path: Path) -> None:
    message = make_message_stop()
    send_message(socket_path, message)


def quit_(socket_path: Path) -> None:
    message = make_message_quit()
    send_message(socket_path, message)


def main() -> None:
    args = parse_args()
    with open(args.config, "r") as conf:
        config: dict = yaml.safe_load(conf)

    socket_ = args.socket or config["socket"]
    create_pipe(socket_)

    command = args.subparser_command
    if command == STOP:
        stop(socket_)
    elif command == PLAY:
        play(socket_, args.station)
    elif command == QUIT:
        quit_(socket_)
