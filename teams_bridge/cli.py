"""Command-line tool."""
import json
import logging
import asyncio
import threading
import time

import rumps
import websockets
from ruamel.yaml import YAML, YAMLError

from __version__ import __version__

TEAMS_MESSAGE_MEETING_UPDATE = "meetingUpdate"

TEAMS_MESSAGE_TOKEN_REFRESH = "tokenRefresh"


class TeamsBridge:
    """Teams bridge application."""

    def __init__(self):
        self.config = {
            "app_name": "Teams Bridge"
        }
        self.app = rumps.App(self.config["app_name"])
        self.set_up_menu()
        self.configuration: dict = {}
        self.read_configuration()

    @property
    def token(self) -> str:
        """Return token if none, otherwise an empty string."""
        return self.configuration["token"] if self.configuration and "token" in self.configuration else ""

    def set_up_menu(self):
        self.app.title = "🥷"

    def start_system_tray_app(self):
        # self.app = rumps.App('VPN', quit_button=None)
        # self.app.menu = [
        #     rumps.MenuItem('Quit', callback=self.disconnect_vpn),
        # ]
        self.app.run()

    def start_updater_thread(self):
        websocket_thread = threading.Thread(target=self.start_websocket_thread)
        websocket_thread.start()

    def start_websocket_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.websocket_handler())

    async def websocket_handler(self):
        uri = f"ws://localhost:8124?token={self.token}&protocol-version=2.0.0&manufacturer=SubspaceSoftware&device=Mac&app=TeamsBridge&app-version=2.0.26"

        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    if not self.token:
                        await websocket.send("{\"action\":\"pair\",\"parameters\":{},\"requestId\":1}")

                    # Your WebSocket logic here
                    message: str | bytes = await websocket.recv()
                    print(f"Received message: {message}")
                    await self.process_message(message)

                    time.sleep(2.0)
                except websockets.exceptions.ConnectionClosedError:
                    pass

    def run(self):
        self.start_updater_thread()
        self.start_system_tray_app()

    async def process_message(self, message: str | bytes):
        """Process an incoming message from Teams."""
        if isinstance(message, str):
            decoded_message: dict = json.loads(message)
            if TEAMS_MESSAGE_TOKEN_REFRESH in decoded_message:
                await self.process_token_refresh(decoded_message[TEAMS_MESSAGE_TOKEN_REFRESH])
            if TEAMS_MESSAGE_MEETING_UPDATE in decoded_message:
                await self.process_meeting_update(decoded_message[TEAMS_MESSAGE_MEETING_UPDATE])

    async def process_token_refresh(self, token: str):
        """Process a token refresh message."""
        # Example: {"tokenRefresh":"1273d305-d1a5-4484-b623-a65467a72a50"}
        if token:
            self.configuration['token'] = token
            print("token=" + token)
            self.write_configuration()

    async def process_meeting_update(self, meeting_update: dict):
        """Process a meeting update message."""
        # Example: {"meetingUpdate":{"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
        # Example: {"meetingUpdate":{"meetingState":{"isMuted":false,"isVideoOn":false,"isHandRaised":false,"isInMeeting":false,"isRecordingOn":false,"isBackgroundBlurred":false,"isSharing":false,"hasUnreadMessages":false},"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
        pass

    def read_configuration(self):
        """Read application configuration from file."""
        try:
            with open("teams_bridge.yaml") as stream:
                try:
                    yaml = YAML(typ='safe')
                    self.configuration = yaml.load(stream)
                except YAMLError as exc:
                    print(exc)
        except OSError as error:
            print(error)

    def write_configuration(self):
        """Write configuration to file."""
        try:
            with open("teams_bridge.yaml", mode='w') as stream:
                yaml = YAML(typ='safe')
                yaml.default_flow_style = False
                yaml.dump(self.configuration, stream)
        except OSError as error:
            print(error)


def main():
    """Execute command line tool."""
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Teams Bridge (version {__version__})...")
    app = TeamsBridge()
    app.run()


if __name__ == "__main__":
    main()
