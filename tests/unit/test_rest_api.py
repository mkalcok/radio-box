"""Unit Tests for radio_box/rest_api.py"""
from typing import Dict, Union
from unittest.mock import ANY, MagicMock

import pytest
from flask.testing import FlaskClient

from radio_box import rest_api

URL_ROOT = "/"
URL_PLAY = "/play"
URL_STOP = "/stop"
URL_STATIONS = "/stations"


def test_index(mocker, rest_client: FlaskClient):
    """Test root URL returning static frontend."""
    send_from_directory = mocker.patch.object(rest_api, "send_from_directory")
    rest_client.get(URL_ROOT)
    send_from_directory.assert_called_once_with("static", "index.html")


@pytest.mark.parametrize(
    "data, status, message",
    [
        ({"station": "example_fm"}, 200, b"OK"),
        ({"station": "bad_station"}, 404, b"Station 'bad_station' not found."),
        ("non_json_data", 400, b"Missing json data."),
    ],
)
def test_play(
    rest_client: FlaskClient,
    data: Union[Dict, str],
    status: int,
    message: bytes,
    mocker,
):
    """Test '/play' endpoint.

    Tested scenarios include:
        * Correctly playing recognized station
        * Returning 404 for unknown station
        * Returning 400 if request data is not in json format
    """
    command = MagicMock()
    make_message = mocker.patch.object(
        rest_api, "make_message_play", return_value=command
    )
    send_message = mocker.patch.object(rest_api, "send_message")
    response = rest_client.post(URL_PLAY, json=data)

    assert response.status_code == status
    assert response.data == message

    if response.status_code == 200:
        make_message.assert_called_once_with(data["station"])
        send_message.assert_called_once_with(ANY, command)


def test_stop(rest_client: FlaskClient, mocker):
    """Test that '/stop' endpoint stops current playback."""
    command = MagicMock()
    make_message = mocker.patch.object(
        rest_api, "make_message_stop", return_value=command
    )
    send_message = mocker.patch.object(rest_api, "send_message")

    response = rest_client.get(URL_STOP)

    assert response.status_code == 200
    assert response.data == b"OK"
    make_message.assert_called_once()
    send_message.assert_called_once_with(ANY, command)


def test_stations(rest_client: FlaskClient, stations: Dict):
    """Test '/stations' endpoint that returns list of configured stations."""
    station_mapping = {key: value["name"] for key, value in stations.items()}
    expected_response = {"stations": station_mapping}

    response = rest_client.get(URL_STATIONS)

    assert response.status_code == 200
    assert response.json == expected_response
