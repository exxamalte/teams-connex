"""Tests for autostart."""

from unittest import mock
from unittest.mock import mock_open

from teams_connex.autostart import Autostart
from tests.utils import concatenate_writes


@mock.patch("os.remove")
@mock.patch("os.path.exists")
def test_autostart(mock_path_exists, mock_remove):
    """Test autostart end-to-end."""
    application_name = "test_application"

    autostart = Autostart()
    path_for_application = autostart.base_path + "/" + application_name + ".plist"
    assert autostart.get_path_for_application(application_name) == path_for_application

    # Test if autostart is enabled or disabled.
    mock_path_exists.return_value = True
    assert autostart.is_enabled(application_name)

    mock_path_exists.return_value = False
    assert not autostart.is_enabled(application_name)

    # Test enabling autostart.
    m = mock_open()
    with mock.patch("builtins.open", m):
        autostart.enable(application_name, ["arg1"])
        m.assert_called_once_with(path_for_application, "wb")
        writes = m.return_value.write.mock_calls
        result = concatenate_writes(writes)
        assert result == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            '<plist version="1.0">\n'
            "<dict>\n"
            "\t<key>Label</key>\n"
            "\t<string>test_application</string>\n"
            "\t<key>ProgramArguments</key>\n"
            "\t<array>\n"
            "\t\t<string>arg1</string>\n"
            "\t</array>\n"
            "</dict>\n"
            "</plist>\n"
        )

    # Test disabling autostart.
    mock_path_exists.return_value = True
    autostart.disable(application_name)
    mock_remove.assert_called_once_with(path_for_application)

    mock_path_exists.return_value = False
    mock_remove.reset_mock()
    autostart.disable(application_name)
    mock_remove.assert_not_called()
