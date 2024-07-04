"""Application constants."""

from typing import Final

APPLICATION_NAME: Final = "Teams Bridge"

CONFIGURATION_FILE_NAME: Final = "teams_bridge.yaml"

CONFIGURATION_WEBHOOK_URI: Final = "webhook_uri"
CONFIGURATION_TOKEN: Final = "token"

MEETING_UPDATE_LAST_MESSAGE: Final = "last_message"
MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS: Final = 30

TEAMS_MESSAGE_MEETING_UPDATE: Final = "meetingUpdate"
TEAMS_MESSAGE_TOKEN_REFRESH: Final = "tokenRefresh"

WEBHOOK_URI_SAMPLE: Final = "http://your-home-assistant:8123/api/webhook/some_hook_id"

WEBSOCKET_HOSTNAME: Final = "localhost"
WEBSOCKET_PORT: Final = 8124
WEBSOCKET_MANUFACTURER: Final = "SubspaceSoftware"
WEBSOCKET_APPLICATION_NAME: Final = "TeamsBridge"
WEBSOCKET_APPLICATION_VERSION: Final = "1"

WEBSOCKET_SLEEP_IN_SECONDS: Final = 2.0
WEBSOCKET_SLEEP_BEFORE_RECONNECT_IN_SECONDS: Final = 10.0
