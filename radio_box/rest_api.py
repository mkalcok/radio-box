import yaml
from flask import abort, jsonify, Flask, request, Response

from radio_box.common import (
    create_pipe,
    send_message,
    make_message_play,
    make_message_stop,
)


def create_app(test_config=None):
    with open("/etc/radio-box/conf.yaml", "r") as conf:
        config = yaml.safe_load(conf)

    socket_path = create_pipe(config["socket"])
    app = Flask(__name__)

    @app.route("/play", methods=["POST"])
    def play():
        station = request.json["station"]
        if station not in config["stations"]:
            abort(Response("Station '{}' not found".format(station),
                           status=404))

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
        return jsonify({"stations": config["stations"]})

    return app
