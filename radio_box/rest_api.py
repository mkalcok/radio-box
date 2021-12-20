import yaml
from flask import Flask, Response, abort, jsonify, request, send_from_directory

from radio_box.common import (
    create_pipe,
    make_message_play,
    make_message_stop,
    send_message,
)


def create_app(test_config=None):
    with open("/etc/radio-box/conf.yaml", "r") as conf:
        config = yaml.safe_load(conf)

    socket_path = create_pipe(config["socket"])
    app = Flask(__name__, static_url_path="", static_folder="static")

    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory("static", "index.html")

    @app.route("/play", methods=["POST"])
    def play():
        station = request.json["station"]
        if station not in config["stations"]:
            abort(Response("Station '{}' not found".format(station), status=404))

        play_command = make_message_play(station)
        send_message(socket_path, play_command)
        return Response("OK", status=200)

    @app.route("/stop", methods=["GET"])
    def stop():
        stop_command = make_message_stop()
        send_message(socket_path, stop_command)

        return Response("OK", status=200)

    @app.route("/stations", methods=["GET"])
    def stations():
        station_data = config["stations"]
        all_stations = {key: value["name"] for key, value in station_data.items()}
        return jsonify({"stations": all_stations})

    return app
