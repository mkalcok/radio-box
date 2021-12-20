"""Common function shared by other modules in radio_box package."""
import argparse
import errno
import os
from pathlib import Path
from typing import Union

from radio_box.protocol import controls_pb2 as controls


def common_argument_parser(parser_description: str) -> argparse.ArgumentParser:
    """Return parser with preconfigured common CLI arguments.

    :param parser_description: Description of CLI tool for which the arguments are
        generated.
    """
    parser = argparse.ArgumentParser(description=parser_description)

    parser.add_argument(
        "-c", "--config", default="/etc/radio-box/conf.yaml", help="Config file path"
    )
    parser.add_argument(
        "-s",
        "--socket",
        help="Communication socket with radio-box service.",
        required=False,
    )

    return parser


def create_pipe(pipe_path: Union[str, Path]) -> Path:
    """Create named pipe if it does not already exist.

    :param pipe_path: Path where named pipe will be created.
    """
    pipe_path = Path(pipe_path)
    try:
        os.mkfifo(pipe_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        print(f"Pipe {pipe_path.absolute()} already exists.")

    return pipe_path.absolute()


def make_message_play(station: str) -> controls.Command:
    """Generate "Play" command for radio-box service.

    This returns a protobuf message that needs to be serialized and written to the
    named pipe on which the radio-box service listens.

    :param station: ID of a radio station thatn should start playing.
        This ID must be key of a station defined in the config file.
    """
    command = controls.Command()
    command.play.type = controls.PLAY
    command.play.station = station

    return command


def make_message_stop() -> controls.Command:
    """Generate "Stop" command for radio-box service.

    This returns a protobuf message that needs to be serialized and written to the
    named pipe on which the radio-box service listens.
    """
    command = controls.Command()
    command.stop.type = controls.STOP

    return command


def make_message_quit() -> controls.Command:
    """Generate command that makes the radio-box service quit,

    This returns a protobuf message that needs to be serialized and written to the
    named pipe on which the radio-box service listens.
    """
    command = controls.Command()
    command.quit.type = controls.QUIT

    return command


def send_message(socket_path: Path, message: controls.Command) -> None:
    """Write protobuf message to the named pipe.

    :param socket_path: Path to the named pipe.
    :param message: Protobuf message.
    """
    with open(socket_path, "wb") as pipe:
        pipe.write(message.SerializeToString())
