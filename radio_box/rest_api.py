"""Simple REST Api interface for controlling radio-box service."""
import os
from typing import Dict, Optional

import yaml
from flask import Flask, Response, abort, jsonify, request, send_from_directory

from radio_box.common import (
    create_pipe,
    make_message_play,
    make_message_stop,
    send_message,
)


def create_app(
    test_config: Optional[Dict] = None,  # pylint: disable=unused-argument
) -> Flask:
    """Initialize flask app."""
    conf_file = os.environ.get("RADIO_BOX_CONF") or "/etc/radio-box/conf.yaml"
    static_folder = os.environ.get("RADIO_BOX_WEB_STATIC") or "static"
    with open(conf_file, "r", encoding="utf8") as conf:
        config = yaml.safe_load(conf)

    socket_path = create_pipe(config["socket"])
    app = Flask(__name__, static_url_path="", static_folder=static_folder)

    @app.route("/", methods=["GET"])
    def index() -> Response:
        """Redirect root url to static frontend."""
        return send_from_directory(static_folder, "index.html")

    @app.route("/play", methods=["POST"])
    def play() -> Response:
        """Play selected station.

        Station ID is expected to be supplied in json form and contain ID that matches
        one station IDs returned by the '/stations' endpoint.
        Example:
            {'station': 'best_radio'}
        """
        data = request.json
        if not isinstance(data, dict):
            abort(Response("Missing json data.", status=400))

        station = data.get("station", "")
        if station not in config["stations"]:
            abort(Response(f"Station '{station}' not found.", status=404))

        play_command = make_message_play(station)
        send_message(socket_path, play_command)
        return Response("OK", status=200)

    @app.route("/stop", methods=["GET"])
    def stop() -> Response:
        """Stop current playback."""
        stop_command = make_message_stop()
        send_message(socket_path, stop_command)

        return Response("OK", status=200)

    @app.route("/stations", methods=["GET"])
    def stations() -> Response:
        """Return list of all pre-configured radio stations."""
        station_data = config["stations"]
        all_stations = {key: value["name"] for key, value in station_data.items()}
        return jsonify({"stations": all_stations})

    return app
