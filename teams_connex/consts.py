"""Application constants."""

from typing import Final

APPLICATION_NAME: Final = "Teams Connex"
APPLICATION_SHORTENED_NAME: Final = "TeamsConnex"
APPLICATION_HOMEPAGE: Final = "https://neon.ninja/teams-connex/"

CONFIGURATION_FILE_NAME: Final = "teams_connex.yaml"

CONFIGURATION_SETTINGS: Final = "settings"
CONFIGURATION_WEBHOOK_URI: Final = "webhook_uri"
CONFIGURATION_TEAMS_TOKEN: Final = "teams_token"
CONFIGURATION_DEBUG_MODE: Final = "debug_mode"

MEETING_UPDATE_LAST_MESSAGE: Final = "last_message"
MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS: Final = 30

TEAMS_MESSAGE_MEETING_UPDATE: Final = "meetingUpdate"
TEAMS_MESSAGE_TOKEN_REFRESH: Final = "tokenRefresh"

WEBHOOK_URI_SAMPLE: Final = "http://your-home-assistant:8123/api/webhook/some_hook_id"

WEBSOCKET_HOSTNAME: Final = "localhost"
WEBSOCKET_PORT: Final = 8124
WEBSOCKET_MANUFACTURER: Final = "NeonNinjaSoftware"
WEBSOCKET_APPLICATION_NAME: Final = APPLICATION_SHORTENED_NAME
WEBSOCKET_APPLICATION_VERSION: Final = "1"

WEBSOCKET_PAIRING_REQUEST_BACKOFF_IN_SECONDS: Final = 2.0
WEBSOCKET_SLEEP_BEFORE_RECONNECT_IN_SECONDS: Final = 10.0
