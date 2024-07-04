"""Teams bridge."""
import asyncio
import json
import logging
import os
import threading
import time
from json import JSONDecodeError

import rumps
import websockets
from ruamel.yaml import YAML, YAMLError

from .consts import TEAMS_MESSAGE_TOKEN_REFRESH, TEAMS_MESSAGE_MEETING_UPDATE, CONFIGURATION_FILE_NAME, \
    CONFIGURATION_WEBHOOK_URI, CONFIGURATION_TOKEN, WEBHOOK_URI_SAMPLE, APPLICATION_NAME

_LOGGER = logging.getLogger(__name__)


class TeamsBridge:
    """Teams bridge."""

    def __init__(self):
        """Initialise Teams bridge application."""
        self.app = rumps.App(APPLICATION_NAME)
        self.set_up_menu()
        self.configuration: dict = {}
        self.read_configuration()

    @property
    def token(self) -> str:
        """Return token if known, otherwise an empty string."""
        return self.configuration[
            CONFIGURATION_TOKEN] if self.configuration and CONFIGURATION_TOKEN in self.configuration else ""

    @token.setter
    def token(self, new_token):
        """Set new token."""
        if new_token:
            self.configuration[CONFIGURATION_TOKEN] = new_token
            self.write_configuration()

    @property
    def webhook_uri(self) -> str:
        """Return webhook uri if known, otherwise an empty string."""
        return self.configuration[
            CONFIGURATION_WEBHOOK_URI] if self.configuration and CONFIGURATION_WEBHOOK_URI in self.configuration else ""

    @webhook_uri.setter
    def webhook_uri(self, new_webhook_uri):
        """Set new webhook uri."""
        if new_webhook_uri and new_webhook_uri != WEBHOOK_URI_SAMPLE:
            self.configuration[CONFIGURATION_WEBHOOK_URI] = new_webhook_uri
            self.write_configuration()

    def set_up_menu(self):
        """Set up system tray menu."""
        self.app.title = "🥷"
        self.app.menu = [rumps.MenuItem(title="Settings...", callback=self.settings)]

    def start_system_tray_app(self):
        """Start system tray application."""
        self.app.run()

    def settings(self, sender):
        """Show settings dialogue."""
        settings_window = rumps.Window("Enter the Webhook URL here", "Settings", WEBHOOK_URI_SAMPLE, dimensions=(320, 20))
        response = settings_window.run()
        if response.clicked:
            text_entered = str(response.text)
            _LOGGER.debug("URL entered: %s", text_entered)
            self.webhook_uri = text_entered
            if text_entered != WEBHOOK_URI_SAMPLE:
                self.configuration[CONFIGURATION_WEBHOOK_URI] = text_entered
                self.write_configuration()

    def start_updater_thread(self):
        """Start websocket updater thread."""
        websocket_thread = threading.Thread(target=self.start_websocket_thread)
        websocket_thread.start()

    def start_websocket_thread(self):
        """Start websocket thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_handler())

    async def websocket_handler(self):
        """Handle websocket messages."""
        uri = f"ws://localhost:8124?token={self.token}&protocol-version=2.0.0&manufacturer=SubspaceSoftware&device=Mac&app=TeamsBridge&app-version=2.0.26"
        # Outer loop is ensuring that the application is reconnecting to Teams if the connection is completely lost.
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    # Inner loop is ensuring that the websocket connection is opened once and kept open.
                    while True:
                        try:
                            if not self.token:
                                _LOGGER.debug("Sending pairing request")
                                await websocket.send("{\"action\":\"pair\",\"parameters\":{},\"requestId\":1}")

                            # Your WebSocket logic here
                            message: str | bytes = await websocket.recv()
                            _LOGGER.debug("Received message: %s", message)
                            await self.process_message(message)

                            time.sleep(2.0)
                        except websockets.exceptions.ConnectionClosedOK as exc:
                            _LOGGER.debug("Websocket connection closed ok: %s", exc)
                            break
                        except websockets.exceptions.ConnectionClosedError as exc:
                            _LOGGER.debug("Websocket connection closed error: %s", exc)
                            break
            except OSError as exc:
                _LOGGER.debug("Websocket connection failed: %s", exc)
                time.sleep(10.0)

    def run(self):
        """Run application components."""
        self.start_updater_thread()
        self.start_system_tray_app()

    async def process_message(self, message: str | bytes):
        """Process an incoming message from Teams."""
        if isinstance(message, str):
            try:
                decoded_message: dict = json.loads(message)
                if TEAMS_MESSAGE_TOKEN_REFRESH in decoded_message:
                    await self.process_token_refresh(decoded_message[TEAMS_MESSAGE_TOKEN_REFRESH])
                if TEAMS_MESSAGE_MEETING_UPDATE in decoded_message:
                    await self.process_meeting_update(decoded_message[TEAMS_MESSAGE_MEETING_UPDATE])
            except JSONDecodeError as exc:
                _LOGGER.warning("Unable to decode message: %s", exc)

    async def process_token_refresh(self, token: str):
        """Process a token refresh message."""
        # Example: {"tokenRefresh":"1273d305-d1a5-4484-b623-a65467a72a50"}
        _LOGGER.info("Processing token refresh: %s", token)
        self.token = token
        # if token:
        #     self.configuration[CONFIGURATION_TOKEN] = token
        #     self.write_configuration()

    async def process_meeting_update(self, meeting_update: dict):
        """Process a meeting update message."""
        # Example: {"meetingUpdate":{"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
        # Example: {"meetingUpdate":{"meetingState":{"isMuted":false,"isVideoOn":false,"isHandRaised":false,"isInMeeting":false,"isRecordingOn":false,"isBackgroundBlurred":false,"isSharing":false,"hasUnreadMessages":false},"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}

        _LOGGER.info("Processing meeting update: %s", meeting_update)

    def read_configuration(self):
        """Read application configuration from file."""
        try:
            if os.path.isfile(CONFIGURATION_FILE_NAME):
                with open(CONFIGURATION_FILE_NAME) as stream:
                    try:
                        yaml = YAML(typ='safe')
                        configuration = yaml.load(stream)
                        self.configuration = configuration if configuration else {}
                    except YAMLError as exc:
                        _LOGGER.warning("Unable to read configuration: %s", exc)
        except OSError as error:
            _LOGGER.warning("Unable to read configuration from file: %s", error)

    def write_configuration(self):
        """Write configuration to file."""
        try:
            with open(CONFIGURATION_FILE_NAME, mode='w') as stream:
                yaml = YAML(typ='safe')
                yaml.default_flow_style = False
                yaml.dump(self.configuration, stream)
        except OSError as error:
            _LOGGER.warning("Unable to write configuration to file: %s", error)
