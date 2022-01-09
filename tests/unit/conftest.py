"""Pytest fixtures."""
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from radio_box import rest_api, service


@pytest.fixture(scope="session")
def common_parser_options() -> List[str]:
    """Provide list of common CLI arguments.

    These are shared by all executables within this package.
    """
    return ["-c", "--config", "-s", "--socket"]


@pytest.fixture(scope="session")
def stations() -> Dict:
    """Provide example configuration of radio stations."""
    return {
        "example_fm": {"url": "http://example.org/stream.mp3", "name": "Example FM"}
    }


@pytest.fixture()
def vlc_instance(mocker) -> MagicMock:
    """Mock objects from VLC library used in radio_box.service.Tuner class."""
    media_player_mock = MagicMock()
    vlc_instance_mock = MagicMock()
    vlc_instance_mock.media_player_new.return_value = media_player_mock
    mocker.patch.object(service.vlc, "Instance", return_value=vlc_instance_mock)

    return vlc_instance_mock


@pytest.fixture
def rest_client(mocker, stations) -> FlaskClient:
    """Provide rest client for api testing."""
    config = {"stations": stations, "socket": "/tmp/foo.pipe"}
    mocker.patch.object(rest_api.yaml, "safe_load", return_value=config)
    mocker.patch.object(rest_api, "create_pipe")

    with patch("builtins.open"):
        app = rest_api.create_app({"TESTING": True})
        with app.test_client() as client:
            yield client
