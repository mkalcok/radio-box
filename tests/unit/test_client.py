"""Unit Tests for radio_box/client.py."""
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, call, patch

import pytest

from radio_box.client import PLAY, QUIT, STOP, main, parse_args, play, quit_, stop, yaml


def test_parse_args(mocker):
    """Test that argument parser is configured with correct description and options."""
    expected_description = "Radio-box CLI client"
    expected_play_positional_arg = "station"
    expected_playpositional_arg_help = "Station name to play"

    mock_argument_parser = MagicMock()
    mock_subparser = MagicMock()
    subparser_play = MagicMock()
    subparser_stop = MagicMock()
    subparser_quit = MagicMock()

    mock_common_argument_parser = mocker.patch(
        "radio_box.client.common_argument_parser", return_value=mock_argument_parser
    )
    mock_argument_parser.add_subparsers.return_value = mock_subparser
    mock_subparser.add_parser.side_effect = [
        subparser_play,
        subparser_stop,
        subparser_quit,
    ]
    parse_args()

    # Assert common argument parser is created
    mock_common_argument_parser.asser_called_once_with(expected_description)
    # Assert subparsers are created
    mock_argument_parser.add_subparsers.assert_called_once_with(
        title="commands", dest="subparser_command"
    )
    # Assert proper subparsers are added
    mock_subparser.add_parser.assert_has_calls(
        [call(arg) for arg in [PLAY, STOP, QUIT]]
    )
    # Assert positional option "station" is added to PLAY subparser
    subparser_play.add_argument.assert_called_once_with(
        expected_play_positional_arg, help=expected_playpositional_arg_help
    )


def test_play(mocker):
    """Test that client writes "play" command into the named pipe."""
    socket_path = Path("/tmp/foo.pipe")
    station = "bar radio"
    message_mock = MagicMock()
    mock_make_message_play = mocker.patch(
        "radio_box.client.make_message_play", return_value=message_mock
    )
    mock_send_message = mocker.patch("radio_box.client.send_message")

    play(socket_path, station)

    mock_make_message_play.assert_called_once_with(station)
    mock_send_message.assert_called_once_with(socket_path, message_mock)


def test_stop(mocker):
    """Test that client writes "stop" command into the named pipe."""
    socket_path = Path("/tmp/foo.pipe")
    message_mock = MagicMock()
    mock_make_message_stop = mocker.patch(
        "radio_box.client.make_message_stop", return_value=message_mock
    )
    mock_send_message = mocker.patch("radio_box.client.send_message")

    stop(socket_path)

    mock_make_message_stop.assert_called_once()
    mock_send_message.assert_called_once_with(socket_path, message_mock)


def test_quit_(mocker):
    """Test that client writes "quit" command into the named pipe."""
    socket_path = Path("/tmp/foo.pipe")
    message_mock = MagicMock()
    mock_make_message_quit = mocker.patch(
        "radio_box.client.make_message_quit", return_value=message_mock
    )
    mock_send_message = mocker.patch("radio_box.client.send_message")

    quit_(socket_path)

    mock_make_message_quit.assert_called_once()
    mock_send_message.assert_called_once_with(socket_path, message_mock)


@pytest.mark.parametrize(
    "action, function, arguments",
    [
        (PLAY, "play", {"station": "foo station"}),
        (STOP, "stop", {}),
        (QUIT, "quit_", {}),
    ],
)
def test_main_actions(action: str, function: str, arguments: Dict, mocker):
    """Test execution of the main function with all supported commands.

    This test mimics user executing CLI client with proper arguments for supported
    actions/sub-commands.
    """
    # Create CLI arguments placeholder
    socket_ = "/tmp/foo.pipe"
    config = "/etc/bar.conf"
    mock_args = MagicMock()
    mock_args.config = config
    mock_args.socket = socket_
    mock_args.subparser_command = action
    for arg, value in arguments.items():
        setattr(mock_args, arg, value)

    mock_arg_parser = mocker.patch(
        "radio_box.client.parse_args", return_value=mock_args
    )
    mock_create_pipe = mocker.patch("radio_box.client.create_pipe")
    mock_expected_function = mocker.patch("radio_box.client." + function)
    mocker.patch.object(yaml, "safe_load", return_value={})

    with patch("builtins.open"):
        main()

    mock_arg_parser.assert_called_once()
    mock_create_pipe.assert_called_once_with(socket_)
    mock_expected_function.assert_called_once_with(socket_, **arguments)


def test_main_socket_location_from_config(mocker):
    """Test that client loads socket location from config if it's not in CLI args."""
    socket_path = "/tmp/foo.pipe"
    mock_args = MagicMock()
    mock_args.config = "/etc/foo.conf"
    mock_args.subparser_command = STOP
    mock_args.socket = None

    mocker.patch("radio_box.client.parse_args", return_value=mock_args)
    mock_create_pipe = mocker.patch("radio_box.client.create_pipe")
    mock_function = mocker.patch("radio_box.client.stop")
    mocker.patch.object(yaml, "safe_load", return_value={"socket": socket_path})

    with patch("builtins.open"):
        main()

    mock_create_pipe.assert_called_once_with(socket_path)
    mock_function.assert_called_once_with(socket_path)


def test_main_socket_location_arg_override(mocker):
    """Test that socket location supplied in CLI argument supersedes the config value."""
    config_socket_path = "/tmp/foo.pipe"
    arg_socket_path = "/tmp/bar.pipe"
    mock_args = MagicMock()
    mock_args.config = "/etc/foo.conf"
    mock_args.subparser_command = STOP
    mock_args.socket = arg_socket_path

    mocker.patch("radio_box.client.parse_args", return_value=mock_args)
    mock_create_pipe = mocker.patch("radio_box.client.create_pipe")
    mock_function = mocker.patch("radio_box.client.stop")
    mocker.patch.object(yaml, "safe_load", return_value={"socket": config_socket_path})

    with patch("builtins.open"):
        main()

    mock_create_pipe.assert_called_once_with(arg_socket_path)
    mock_function.assert_called_once_with(arg_socket_path)
