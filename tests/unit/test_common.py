"""Unit Tests for radio_box/common.py."""
import errno
import os
from pathlib import Path
from typing import List
from unittest.mock import call, mock_open, patch

import pytest
from pytest import mark

from radio_box.common import (
    common_argument_parser,
    create_pipe,
    make_message_play,
    make_message_quit,
    make_message_stop,
    send_message,
)


def test_common_argument_parser(common_parser_options: List):
    """Test that common argument parser has expected options."""
    description = "FooBar"
    parser = common_argument_parser(description)
    parser_options = parser._option_string_actions

    assert parser.description == description
    assert all(option in parser_options for option in common_parser_options)


@mark.parametrize("file_exists", [False, True])
def test_create_pipe(file_exists, mocker):
    """Test creation of named pipe used for communication between components.

    If named pipe already exists, this function should pass without errors.
    """
    input_path = "./foo/bar.pipe"
    expected_path = Path(input_path).absolute()
    mocker.patch("os.mkfifo")

    if file_exists:
        file_exists_error = OSError()
        file_exists_error.errno = errno.EEXIST
        os.mkfifo.side_effect = file_exists_error

    pipe_path = create_pipe(expected_path)

    os.mkfifo.assert_called_once_with(expected_path)
    assert pipe_path == expected_path


def test_create_pipe_fail(mocker):
    """Test that exception is raised if theres problem when creating a pipe.

    Exception to this behaviour is EEXIST error which should be passed silently.
    """
    error = OSError()
    error.errno = errno.EPERM
    mocker.patch("os.mkfifo", side_effect=error)

    with pytest.raises(OSError):
        create_pipe("/tmp/foo.pipe")


def test_make_message_play():
    """Test creation of "play" protobuf message."""
    station = "fooRadio"
    message = make_message_play(station)

    assert hasattr(message, "play")
    assert message.play.station == station


def test_make_message_stop():
    """Test creation of "stop" protobuf message."""
    message = make_message_stop()

    assert hasattr(message, "stop")


def test_make_message_quit():
    """Test creation of "quit" protobuf message."""
    message = make_message_quit()

    assert hasattr(message, "quit")


def test_send_message():
    """Test writing protobuf message into named pipe."""
    message = make_message_stop()
    pipe_path = Path("/tmp/foo.pip")

    pipe_mock = mock_open()
    pipe_handle = pipe_mock()  # This handle will have `write()` calls
    with patch("builtins.open", pipe_mock):
        send_message(pipe_path, message)

    pipe_mock.assert_has_calls([call(pipe_path, "wb")])
    pipe_handle.write.assert_called_once_with(message.SerializeToString())
