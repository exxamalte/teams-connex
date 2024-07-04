"""Teams bridge."""
import asyncio
import json
import logging
import os
import threading
import time
from json import JSONDecodeError

import httpx
import platformdirs
import rumps
import websockets
from expiringdict import ExpiringDict
from ruamel.yaml import YAML, YAMLError

from teams_bridge.consts import TEAMS_MESSAGE_TOKEN_REFRESH, TEAMS_MESSAGE_MEETING_UPDATE, CONFIGURATION_FILE_NAME, \
    CONFIGURATION_WEBHOOK_URI, CONFIGURATION_TOKEN, WEBHOOK_URI_SAMPLE, APPLICATION_NAME, WEBSOCKET_HOSTNAME, \
    WEBSOCKET_PORT, WEBSOCKET_MANUFACTURER, WEBSOCKET_APPLICATION_NAME, WEBSOCKET_APPLICATION_VERSION, \
    MEETING_UPDATE_LAST_MESSAGE, MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS, WEBSOCKET_SLEEP_BEFORE_RECONNECT_IN_SECONDS, \
    WEBSOCKET_SLEEP_IN_SECONDS

_LOGGER = logging.getLogger(__name__)


class TeamsBridge:
    """Teams bridge."""

    def __init__(self):
        """Initialise Teams bridge application."""
        self.app = rumps.App(APPLICATION_NAME)
        self.set_up_menu()
        self.configuration_file = os.path.join(platformdirs.user_data_dir(appname=APPLICATION_NAME, ensure_exists=True), CONFIGURATION_FILE_NAME)
        self.configuration: dict = {}
        self.read_configuration()
        self._websocket_connected: bool = False
        self.meeting_update_cache = ExpiringDict(max_len=1, max_age_seconds=MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS)

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

    @property
    def websocket_connected(self) -> bool:
        """Return if websocket is connected."""
        return self._websocket_connected

    @websocket_connected.setter
    def websocket_connected(self, connected: bool):
        """Set status if websocket is connected or not."""
        self._websocket_connected = connected
        self.app.title = "🥷🟢" if connected else "🥷⚪️"

    def set_up_menu(self):
        """Set up system tray menu."""
        self.app.title = "🥷"
        self.app.menu = [rumps.MenuItem(title="Settings...", callback=self.settings)]

    def start_system_tray_app(self):
        """Start system tray application."""
        self.app.run()

    def settings(self, sender):
        """Show settings dialogue."""
        webhook_uri = self.webhook_uri if self.webhook_uri else WEBHOOK_URI_SAMPLE
        settings_window = rumps.Window("Enter the Webhook URL here", "Settings", webhook_uri, dimensions=(640, 20))
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
        uri = f"ws://{WEBSOCKET_HOSTNAME}:{WEBSOCKET_PORT}?token={self.token}&protocol-version=2.0.0&manufacturer={WEBSOCKET_MANUFACTURER}&device=Mac&app={WEBSOCKET_APPLICATION_NAME}&app-version={WEBSOCKET_APPLICATION_VERSION}"
        # Outer loop is ensuring that the application is reconnecting to Teams if the connection is completely lost.
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    # Inner loop is ensuring that the websocket connection is opened once and kept open.
                    self.websocket_connected = True
                    while True:
                        try:
                            if not self.token:
                                _LOGGER.debug("Sending pairing request")
                                await websocket.send("{\"action\":\"pair\",\"parameters\":{},\"requestId\":1}")

                            # Reading messages from websocket.
                            message: str | bytes = await websocket.recv()
                            _LOGGER.debug("Received message: %s", message)
                            await self.process_message(message)
                            # Wait 2 seconds before processing more messages.
                            time.sleep(WEBSOCKET_SLEEP_IN_SECONDS)
                        except websockets.exceptions.ConnectionClosedOK as exc:
                            _LOGGER.debug("Websocket connection closed ok: %s", exc)
                            break
                        except websockets.exceptions.ConnectionClosedError as exc:
                            _LOGGER.debug("Websocket connection closed error: %s", exc)
                            break
            except OSError as exc:
                _LOGGER.debug("Websocket connection failed: %s", exc)
                self.websocket_connected = False
                # Wait for 10 seconds before reconnecting.
                time.sleep(WEBSOCKET_SLEEP_BEFORE_RECONNECT_IN_SECONDS)

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
                    await self.process_meeting_update(decoded_message)
            except JSONDecodeError as exc:
                _LOGGER.warning("Unable to decode message: %s", exc)

    async def process_token_refresh(self, token: str):
        """Process a token refresh message."""
        # Example: {"tokenRefresh":"1273d305-d1a5-4484-b623-a65467a72a50"}
        _LOGGER.info("Processing token refresh: %s", token)
        self.token = token

    async def process_meeting_update(self, meeting_update: dict):
        """Process a meeting update message."""
        # Example: {"meetingUpdate":{"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
        # Example: {"meetingUpdate":{"meetingState":{"isMuted":false,"isVideoOn":false,"isHandRaised":false,"isInMeeting":false,"isRecordingOn":false,"isBackgroundBlurred":false,"isSharing":false,"hasUnreadMessages":false},"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
        _LOGGER.info("Processing meeting update: %s", meeting_update)
        # Don't send the same message payload twice in a row within 30 seconds.
        if MEETING_UPDATE_LAST_MESSAGE in self.meeting_update_cache and self.meeting_update_cache[
            MEETING_UPDATE_LAST_MESSAGE] == meeting_update:
            _LOGGER.debug("Ignoring meeting update because it is the same information already sent within the last %s seconds",
                          MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS)
        else:
            if self.webhook_uri:
                # Home Assistant expects:
                # * Method: PUT
                # * Content-Type: application/json
                # * JSON encoded payload
                try:
                    with httpx.Client() as client:
                        headers = {'Content-Type': 'application/json'}
                        # payload = json.dumps(meeting_update)
                        r = client.put(self.webhook_uri, headers=headers, json=meeting_update)
                        _LOGGER.debug("Webhook response: %s", r)
                        # Update cache
                        self.meeting_update_cache[MEETING_UPDATE_LAST_MESSAGE] = meeting_update
                except httpx.RequestError as exc:
                    _LOGGER.error("Webhook error: %s", exc)
            else:
                _LOGGER.warning("Webhook URI is not set.")

    def read_configuration(self):
        """Read application configuration from file."""
        try:
            if os.path.isfile(self.configuration_file):
                with open(self.configuration_file) as stream:
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
            with open(self.configuration_file, mode='w') as stream:
                yaml = YAML(typ='safe')
                yaml.default_flow_style = False
                yaml.dump(self.configuration, stream)
        except OSError as error:
            _LOGGER.warning("Unable to write configuration to file: %s", error)
