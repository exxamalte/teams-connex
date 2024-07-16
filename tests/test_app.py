"""Test for the main app."""

from unittest import mock
from unittest.mock import mock_open

from teams_connex.app import TeamsConnex


@mock.patch("os.path.isfile")
def test_app_configuration_defaults(mock_isfile):
    """Test app configuration file defaults."""
    mock_isfile.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        assert app.token == ""
        assert app.webhook_uri == ""
        assert not app.debug_mode


@mock.patch("os.path.isfile")
def test_app_configuration_values(mock_isfile):
    """Test app configuration file defaults."""
    mock_isfile.return_value = True
    m = mock_open(
        read_data="settings:\n"
        "  teams_token: test-token-1\n"
        "  webhook_uri: https://my.webhook.url/\n"
        "  debug_mode: true\n"
    )
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        assert app.token == "test-token-1"
        assert app.webhook_uri == "https://my.webhook.url/"
        assert app.debug_mode
