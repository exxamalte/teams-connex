"""Application constants."""
from typing import Final

CONFIGURATION_FILE_NAME: Final = "teams_bridge.yaml"

CONFIGURATION_WEBHOOK: Final = "webhook"
CONFIGURATION_TOKEN: Final = "token"

TEAMS_MESSAGE_MEETING_UPDATE: Final = "meetingUpdate"
TEAMS_MESSAGE_TOKEN_REFRESH: Final = "tokenRefresh"

WEBHOOK_URI_SAMPLE: Final = "http://your-home-assistant:8123/api/webhook/some_hook_id"
