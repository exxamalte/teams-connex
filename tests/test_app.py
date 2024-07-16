"""Test for the main app."""

from unittest import mock
from unittest.mock import ANY, mock_open

from teams_connex.app import TeamsConnex
from tests.utils import concatenate_writes


@mock.patch("os.path.isdir")
@mock.patch("os.path.isfile")
def test_app_configuration_read_defaults(mock_isfile, mock_isdir):
    """Test app configuration file defaults."""
    mock_isfile.return_value = True
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        assert app.token == ""
        assert app.webhook_uri == ""
        assert not app.debug_mode


@mock.patch("os.path.isfile")
def test_app_configuration_read_custom_values(mock_isfile):
    """Test app configuration file with custom values."""
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


@mock.patch("os.path.isdir")
def test_app_configuration_write_token(mock_isdir):
    """Test write to app configuration file."""
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        # Token
        app.token = "test-token-2"
        m.assert_called_with(app.configuration_file, mode="w")
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == ("settings:\n" "  teams_token: test-token-2\n")


@mock.patch("os.path.isdir")
def test_app_configuration_write_webhook_url(mock_isdir):
    """Test write to app configuration file."""
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        # Webhook URL
        app.webhook_uri = "https://your.webhook.url/"
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == ("settings:\n" "  webhook_uri: https://your.webhook.url/\n")


@mock.patch("os.path.isdir")
def test_app_configuration_write_debug_mode(mock_isdir):
    """Test write to app configuration file."""
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        # Debug mode
        m.reset_mock()
        app.debug_mode = True
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == ("settings:\n" "  debug_mode: true\n")


@mock.patch("os.path.isdir")
def test_app_configuration_write_values(mock_isdir):
    """Test write to app configuration file."""
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        # Token
        app.token = "test-token-2"
        m.assert_called_with(app.configuration_file, mode="w")
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == ("settings:\n" "  teams_token: test-token-2\n")
        # Webhook URL
        m.reset_mock()
        app.webhook_uri = "https://your.webhook.url/"
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == (
            "settings:\n"
            "  teams_token: test-token-2\n"
            "  webhook_uri: https://your.webhook.url/\n"
        )
        # Debug mode
        m.reset_mock()
        app.debug_mode = True
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == (
            "settings:\n"
            "  debug_mode: true\n"
            "  teams_token: test-token-2\n"
            "  webhook_uri: https://your.webhook.url/\n"
        )


@mock.patch("logging.Logger.warning")
@mock.patch("os.path.isdir")
@mock.patch("os.path.isfile")
def test_app_configuration_read_error(mock_isfile, mock_isdir, mock_logger):
    """Test app configuration file defaults."""
    mock_isfile.return_value = True
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    error = OSError("Test error")
    m.side_effect = error
    with mock.patch("builtins.open", m):
        TeamsConnex()
        mock_logger.assert_called_with(ANY, error)


@mock.patch("logging.Logger.warning")
@mock.patch("os.path.isdir")
@mock.patch("os.path.isfile")
def test_app_configuration_write_error(mock_isfile, mock_isdir, mock_logger):
    """Test app configuration file defaults."""
    mock_isfile.return_value = True
    mock_isdir.return_value = True
    m = mock_open(read_data="")
    with mock.patch("builtins.open", m):
        app = TeamsConnex()
        error = OSError("Test error")
        m.side_effect = error
        # Token
        app.token = "test-token-3"
        mock_logger.assert_called_with(ANY, error)
