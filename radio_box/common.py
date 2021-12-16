import errno
import os

from pathlib import Path
from typing import Union

from radio_box.protocol import controls_pb2 as controls


def create_pipe(pipe_path: Union[str, Path]) -> Path:
    pipe_path = Path(pipe_path)
    try:
        os.mkfifo(pipe_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        print("Pipe %s already exists." % pipe_path.absolute())

    return pipe_path.absolute()


def make_message_play(station: str) -> controls.Command:
    command = controls.Command()
    command.play.type = controls.PLAY
    command.play.station = station

    return command


def make_message_stop() -> controls.Command:
    command = controls.Command()
    command.stop.type = controls.STOP

    return command


def make_message_quit() -> controls.Command:
    command = controls.Command()
    command.quit.type = controls.QUIT

    return command


def send_message(socket_path: Path, message: controls.Command) -> None:
    with open(socket_path, "wb") as pipe:
        pipe.write(message.SerializeToString())
