import argparse
from typing import Dict, Optional

import vlc
import yaml
from google.protobuf.message import DecodeError

from radio_box.common import create_pipe
from radio_box.protocol import controls_pb2 as controls

QUIT_ = False


class Tuner:
    def __init__(self, stations: Dict[str, dict]) -> None:
        self.stations = stations
        self.vlc = vlc.Instance("--input-repeat=-1", "-Idummy", "--aout=alsa")
        self.player: vlc.MediaPlayer = self.vlc.media_player_new()
        self.active_media: Optional[vlc.Media] = None

    def set_station(self, station_name: str) -> None:
        station: dict = self.stations.get(station_name)
        if not station:
            raise ValueError(
                "Unknown station {}. Check config file to see if it's"
                "defined.".format(station_name)
            )

        self.active_media: vlc.Media = self.vlc.media_new(station.get("url"))
        self.player.set_media(self.active_media)

    def stop(self):
        self.player.stop()
        if self.active_media:
            print("Stopping current media.")
            self.active_media.release()
            self.active_media = None

    def play(self, station_name: str):
        if self.active_media:
            self.stop()
        print("Starting playback: %s" % station_name)
        self.set_station(station_name)
        self.player.play()


def parse_args() -> argparse.Namespace:
    description = "Radio player for pre-configured Internet radios."
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-c", "--config", default="/etc/radio-box/conf.yaml", help="Config file path"
    )
    parser.add_argument(
        "-s",
        "--socket",
        help="Communication socket with radio-box service.",
        required=False,
    )

    return parser.parse_args()


def process_command(message: controls.Command, tuner: Tuner):
    message_type = message.WhichOneof("sub_command")
    command = getattr(message, message_type)

    if command.type == controls.PLAY:
        tuner.play(command.station)
    elif command.type == controls.STOP:
        tuner.stop()
    elif command.type == controls.QUIT:
        global QUIT_
        QUIT_ = True
    else:
        print("Unknown command %s" % message_type)


def run() -> None:
    args = parse_args()
    with open(args.config, "r") as conf:
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
            except DecodeError as exc:
                print("Failed to parse message: %s" % exc)
                continue


if __name__ == "__main__":
    run()
