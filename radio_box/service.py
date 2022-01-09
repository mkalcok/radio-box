"""RadioBox service that waits commands and plays selected internet radio stations.

Communication is conducted over a named pipe defined in the configuration file. This
service can be controlled either with cli client or rest api, both are part of the
radio_box python package.

This service utilizes VLC player to process audio streams. The VLC player is started
in the headless mode (no GUI required) and audio output is played over a default alsa
audio device.
"""
import argparse
from typing import Dict, Optional

import vlc
import yaml
from google.protobuf.message import DecodeError

from radio_box.common import common_argument_parser, create_pipe
from radio_box.protocol import controls_pb2 as controls

QUIT_ = False


class Tuner:
    """Wrapper for VLC player instance that handles start/stop and media change."""

    def __init__(self, stations: Dict[str, dict]) -> None:
        """Initialize Tuner instance.

        The station parameter expects dict containing station configurations. The
        format of the dict must be {'station_id': {'url': 'station_stream_url'}}.
        Example:
            {'best_radio': {'url': 'http://example.org/best_stream.mp3'}}

        :param stations: dict containing station configuration.
        """
        self.stations = stations
        self.vlc = vlc.Instance("--input-repeat=-1", "-Idummy", "--aout=alsa")
        self.player: vlc.MediaPlayer = self.vlc.media_player_new()
        self.active_media: Optional[vlc.Media] = None

    def _set_station(self, station_id: str) -> None:
        """Change current station.

        The 'station_id' parameter must be a key from self.stations dict.

        :param station_id: ID of the new station to set as a current media.
        :raises ValueError: If supplied station_id is not found in self.stations.
        """
        station: dict = self.stations.get(station_id, {})
        if not station:
            raise ValueError(
                f"Unknown station {station_id}. Check config file to see if it's"
                "defined."
            )

        self.active_media = self.vlc.media_new(station.get("url"))
        self.player.set_media(self.active_media)

    def stop(self) -> None:
        """Stop current playback."""
        self.player.stop()
        if self.active_media:
            print("Stopping current media.")
            self.active_media.release()
            self.active_media = None

    def play(self, station_id: str) -> None:
        """Starts playback of selected radio station.

        The 'station_id' parameter must be a key from self.stations dict.

        :param station_id: ID of the new station to set as a current media.
        :raises ValueError: If supplied station_id is not found in self.stations.
        """
        if self.active_media:
            self.stop()
        print(f"Starting playback: {station_id}")
        self._set_station(station_id)
        self.player.play()


def parse_args() -> argparse.Namespace:
    """Parse arguments for CLI."""
    parser = common_argument_parser("Radio player for pre-configured Internet radios.")
    return parser.parse_args()


def process_command(message: controls.Command, tuner: Tuner) -> None:
    """Parse and execute command contained in the message.

    :param message: Protobuf message containing command.
    :param tuner: Tuner instance
    """
    message_type = str(message.WhichOneof("sub_command"))
    command = getattr(message, message_type)

    if command.type == controls.PLAY:
        tuner.play(command.station)
    elif command.type == controls.STOP:
        tuner.stop()
    elif command.type == controls.QUIT:
        global QUIT_  # pylint: disable=global-statement
        QUIT_ = True
    else:  # pragma: no cover
        print(f"Unknown command {message_type}")


def run() -> None:
    """Run radio-box service process and await commands."""
    args = parse_args()
    with open(args.config, "r", encoding="utf8") as conf:
        config: dict = yaml.safe_load(conf)

    socket_ = args.socket or config["socket"]

    print("Opening pipe.")
    pipe_path = create_pipe(socket_)
    print("Starting Player.")
    tuner = Tuner(config["stations"])
    print("Radio Box ready.")

    while not QUIT_:
        print("Waiting for commands")
        with open(pipe_path, "rb") as pipe:
            message = controls.Command()
            try:
                message.ParseFromString(pipe.read())
                process_command(message, tuner)
            except DecodeError as exc:  # pragma: no cover
                print(f"Failed to parse message: {exc}")
                continue


if __name__ == "__main__":  # pragma: no cover
    run()
