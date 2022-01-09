"""Unit Tests for radio_box/service.py."""
from typing import Dict
from unittest.mock import MagicMock, mock_open, patch

import pytest

from radio_box import service
from radio_box.protocol import controls_pb2 as controls


def test_tuner_set_station(vlc_instance, stations):
    """Test that Tuner._set_station() updates actively played media."""
    unknown_station_id = "bar"
    known_station_id = list(stations)[0]

    media_mock = MagicMock()
    vlc_instance.media_new.return_value = media_mock

    tuner = service.Tuner(stations)
    tuner._set_station(known_station_id)

    assert tuner.active_media == media_mock
    tuner.player.set_media.assert_called_once_with(media_mock)

    # Test that setting an unknown station raises an error
    with pytest.raises(ValueError):
        tuner._set_station(unknown_station_id)


def test_tuner_stop(vlc_instance, stations):
    """Test that Tuner.stop() stops playback of active media."""
    active_media = MagicMock()

    tuner = service.Tuner(stations)
    tuner.active_media = active_media

    tuner.stop()

    tuner.player.stop.assert_called_once()
    active_media.release.assert_called_once()
    assert tuner.active_media is None

    # Test that if there's no active media, Tuner wont try to release it
    active_media.reset_mock()

    tuner.stop()

    active_media.release.assert_not_called()


def test_tuner_play(mocker, vlc_instance, stations):
    """Test that Tuner.play() starts media playback."""
    set_station_mock = mocker.patch.object(service.Tuner, "_set_station")
    stop_mock = mocker.patch.object(service.Tuner, "stop")
    station_id = list(stations)[0]

    tuner = service.Tuner(stations)
    tuner.active_media = None

    tuner.play(station_id)

    stop_mock.assert_not_called()
    set_station_mock.assert_called_once_with(station_id)
    tuner.player.play.assert_called_once()

    # Test that if there's active media it's stopped before playing a new one.
    set_station_mock.reset_mock()
    tuner.player.reset_mock()

    tuner.active_media = MagicMock()
    tuner.play(station_id)

    stop_mock.assert_called_once()
    set_station_mock.assert_called_once_with(station_id)
    tuner.player.play.assert_called_once()


def test_parse_args(mocker):
    """Test CLI argument parsing of service.run() entrypoint."""
    description = "Radio player for pre-configured Internet radios."
    parser_mock = MagicMock()
    expected_result = MagicMock()
    parser_mock.parse_args.return_value = expected_result

    arg_parser = mocker.patch.object(
        service, "common_argument_parser", return_value=parser_mock
    )

    result = service.parse_args()

    arg_parser.assert_called_once_with(description)
    parser_mock.parse_args.assert_called_once()
    assert result == expected_result


def test_process_command_play():
    """Test processing of a PLAY command."""
    station = "foo"
    tuner = MagicMock()
    message = controls.Command()
    message.play.type = controls.PLAY
    message.play.station = station

    service.process_command(message, tuner)

    tuner.play.assert_called_once()


def test_process_command_stop():
    """Test processing of a STOP command."""
    tuner = MagicMock()
    message = controls.Command()
    message.stop.type = controls.STOP

    service.process_command(message, tuner)

    tuner.stop.assert_called_once()


def test_process_command_quit():
    """Test processing of a QUIT command."""
    tuner = MagicMock()
    message = controls.Command()
    message.quit.type = controls.QUIT

    with patch("radio_box.service.QUIT_", False):
        service.process_command(message, tuner)
        assert service.QUIT_


def test_run(stations: Dict, mocker):
    """Test main execution loop of service.py."""

    def quit_main_loop(*_):
        quit_control.__bool__.return_value = True

    socket_path = "/tmp/foo.pipe"
    conf_path = "/etc/foo.conf"

    message = controls.Command()
    message.quit.type = controls.QUIT

    config = {"stations": stations, "socket": socket_path}

    tuner = MagicMock()
    args = MagicMock()
    args.socket = socket_path
    args.config = conf_path
    mocker.patch.object(service, "parse_args", return_value=args)

    create_pipe_mock = mocker.patch.object(
        service, "create_pipe", return_value=socket_path
    )
    mocker.patch.object(service.yaml, "safe_load", return_value=config)
    tuner_mock = mocker.patch.object(service, "Tuner", return_value=tuner)
    process_command_mock = mocker.patch.object(
        service, "process_command", side_effect=quit_main_loop
    )

    quit_control = mocker.patch.object(service, "QUIT_")
    quit_control.__bool__.return_value = False

    with patch("builtins.open", mock_open(read_data=message.SerializeToString())):
        service.run()

    create_pipe_mock.assert_called_once_with(socket_path)
    tuner_mock.assert_called_once_with(config["stations"])
    process_command_mock.assert_called_once_with(message, tuner)


def test_run_socket_from_args(stations: Dict, mocker):
    """Test that if socket path is supplied in args, it supersedes value from config."""
    socket_path_args = "/tmp/foo.pipe"
    socket_path_conf = "/tmp/bar.pipe"

    args = MagicMock()
    args.socket = socket_path_args
    args.config = "/etc/foo.conf"
    mocker.patch.object(service, "parse_args", return_value=args)

    config = {"stations": stations, "socket": socket_path_conf}

    mocker.patch.object(service.yaml, "safe_load", return_value=config)
    mocker.patch.object(service, "Tuner")
    create_pipe_mock = mocker.patch.object(service, "create_pipe")

    quit_control = mocker.patch.object(service, "QUIT_")
    quit_control.__bool__.return_value = True

    with patch("builtins.open"):
        service.run()

    create_pipe_mock.assert_called_once_with(socket_path_args)
