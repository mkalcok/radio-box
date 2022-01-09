"""CLI client for controlling radio-box service."""

import argparse
from pathlib import Path

import yaml

from radio_box.common import (
    common_argument_parser,
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
    """Parse CLI arguments of radio-box client."""
    parser = common_argument_parser("Radio-box CLI client.")
    subparsers = parser.add_subparsers(title="commands", dest="subparser_command")

    play_parser = subparsers.add_parser(PLAY)
    play_parser.add_argument("station", help="Station name to play")

    subparsers.add_parser(STOP)
    subparsers.add_parser(QUIT)

    return parser.parse_args()


def play(socket_path: Path, station: str) -> None:
    """Tell radio-box service to play selected station.

    Supplied station name should be key of one of the stations defined in the
    configuration file.

    If another station already plays, its playback will be stopped and this station
    will play instead.

    :param socket_path: Path to named pipe on which the radio-box service listens.
    :param station: Name of the station to play.
    """
    message = make_message_play(station)
    send_message(socket_path, message)


def stop(socket_path: Path) -> None:
    """Tell radio-box service to stop current playback.

    :param socket_path: Path to named pipe on which the radio-box service listens.
    """
    message = make_message_stop()
    send_message(socket_path, message)


def quit_(socket_path: Path) -> None:
    """Tell radio-box service to quit completely, killing the service process.

    :param socket_path: Path to named pipe on which the radio-box service listens.
    """
    message = make_message_quit()
    send_message(socket_path, message)


def main() -> None:
    """Process cli command."""
    args = parse_args()
    with open(args.config, "r", encoding="utf8") as conf:
        config: dict = yaml.safe_load(conf)

    socket_ = args.socket or config["socket"]
    create_pipe(socket_)

    command = args.subparser_command
    if command == STOP:
        stop(socket_)
    elif command == PLAY:
        play(socket_, station=args.station)
    elif command == QUIT:
        quit_(socket_)
