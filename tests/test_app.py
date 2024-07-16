"""Test for the main app."""

from unittest import mock
from unittest.mock import mock_open

from teams_connex.app import TeamsConnex


@mock.patch("os.path.isfile")
def test_app(mock_isfile):
    """Test app."""

    mock_isfile.return_value = True

    m = mock_open(read_data="token: abcdefg")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        assert app.token == "abcdefg"
