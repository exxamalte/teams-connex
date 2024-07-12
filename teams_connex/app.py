"""Teams Connex."""

import asyncio
import json
from json import JSONDecodeError
import logging
import os
import sys
import threading
import time
import webbrowser

from expiringdict import ExpiringDict
import httpx
import platformdirs
from ruamel.yaml import YAML, YAMLError
import rumps
import websockets

from teams_connex.__version__ import __version__
from teams_connex.autostart import Autostart
from teams_connex.consts import (
    APPLICATION_HOMEPAGE,
    APPLICATION_NAME,
    CONFIGURATION_FILE_NAME,
    CONFIGURATION_TOKEN,
    CONFIGURATION_WEBHOOK_URI,
    MEETING_UPDATE_LAST_MESSAGE,
    MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS,
    TEAMS_MESSAGE_MEETING_UPDATE,
    TEAMS_MESSAGE_TOKEN_REFRESH,
    WEBHOOK_URI_SAMPLE,
    WEBSOCKET_APPLICATION_NAME,
    WEBSOCKET_APPLICATION_VERSION,
    WEBSOCKET_HOSTNAME,
    WEBSOCKET_MANUFACTURER,
    WEBSOCKET_PAIRING_REQUEST_BACKOFF_IN_SECONDS,
    WEBSOCKET_PORT,
    WEBSOCKET_SLEEP_BEFORE_RECONNECT_IN_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class TeamsConnex:
    """Teams Connex."""

    def __init__(self):
        """Initialise Teams Connex application."""
        self.app = rumps.App(APPLICATION_NAME)
        self.set_up_menu()
        self.configuration_file = os.path.join(
            platformdirs.user_data_dir(appname=APPLICATION_NAME, ensure_exists=True),
            CONFIGURATION_FILE_NAME,
        )
        self._configuration: dict = {}
        self.read_configuration()
        self._websocket_connected: bool = False
        self._websocket_paired: bool = False
        self._websocket_can_pair: bool = False
        self._websocket_pairing_request_cache = ExpiringDict(
            max_len=1, max_age_seconds=WEBSOCKET_PAIRING_REQUEST_BACKOFF_IN_SECONDS
        )
        self._meeting_update_cache = ExpiringDict(
            max_len=1, max_age_seconds=MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS
        )

    @property
    def token(self) -> str:
        """Return token if known, otherwise an empty string."""
        return (
            self._configuration[CONFIGURATION_TOKEN]
            if self._configuration and CONFIGURATION_TOKEN in self._configuration
            else ""
        )

    @token.setter
    def token(self, new_token: str):
        """Set new token."""
        self._configuration[CONFIGURATION_TOKEN] = new_token
        self.write_configuration()

    @property
    def webhook_uri(self) -> str:
        """Return webhook uri if known, otherwise an empty string."""
        return (
            self._configuration[CONFIGURATION_WEBHOOK_URI]
            if self._configuration and CONFIGURATION_WEBHOOK_URI in self._configuration
            else ""
        )

    @webhook_uri.setter
    def webhook_uri(self, new_webhook_uri: str):
        """Set new webhook uri."""
        if new_webhook_uri and new_webhook_uri != WEBHOOK_URI_SAMPLE:
            self._configuration[CONFIGURATION_WEBHOOK_URI] = new_webhook_uri
            self.write_configuration()

    @property
    def websocket_connected(self) -> bool:
        """Return if websocket is connected."""
        return self._websocket_connected

    @websocket_connected.setter
    def websocket_connected(self, connected: bool):
        """Set status if websocket is connected or not."""
        self._websocket_connected = connected
        self.update_statusbar_icon()

    def update_statusbar_icon(self):
        """Update the icon in the status bar."""
        if self.websocket_connected and self.websocket_paired and self.webhook_uri:
            icon = "statusbar-green.png"
        elif self.websocket_connected:
            icon = "statusbar-blue.png"
        else:
            icon = "statusbar-grey.png"
        self.app.icon = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../resources/",
                icon,
            )
        )

    @property
    def websocket_paired(self) -> bool:
        """Return if websocket is paired."""
        return self._websocket_paired

    @websocket_paired.setter
    def websocket_paired(self, paired: bool):
        """Set status if websocket is paired or not."""
        self._websocket_paired = paired
        self.update_statusbar_icon()

    @property
    def websocket_pairing_request_pending(self) -> bool:
        """Return if websocket pairing request is currently pending."""
        return (
            "pairing_request_pending" in self._websocket_pairing_request_cache
            and self._websocket_pairing_request_cache["pairing_request_pending"]
        )

    @websocket_pairing_request_pending.setter
    def websocket_pairing_request_pending(self, pending: bool):
        """Set if websocket pairing request is currently pending."""
        self._websocket_pairing_request_cache["pairing_request_pending"] = pending

    @property
    def start_at_login(self) -> bool:
        """Return if this app is configured to start at login."""
        autostart = Autostart()
        autostart_enabled = autostart.is_enabled(APPLICATION_NAME)
        _LOGGER.debug("Start at login: %s", autostart_enabled)
        return autostart_enabled

    @start_at_login.setter
    def start_at_login(self, new_value: bool):
        """Set application to start at login."""
        autostart = Autostart()
        if new_value:
            executable = self.path_to_executable()
            if executable:
                options = [executable]
                autostart.enable(name=APPLICATION_NAME, program_arguments=options)
                _LOGGER.info("Enabled autostart for executable: %s", executable)
            else:
                _LOGGER.warning(
                    "Not running a self-contained executable. Cannot set up autostart."
                )
                rumps.alert(
                    "Error",
                    f"Cannot set up autostart because you are not running {APPLICATION_NAME} as an application.",
                )
        else:
            autostart.disable(name=APPLICATION_NAME)
            _LOGGER.info("Disabled autostart.")

    @staticmethod
    def path_to_executable() -> str | None:
        """Get path to this application's executable or None if running as a normal Python process."""
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            application_path = sys.executable
            _LOGGER.debug(
                "Running in a bundle, path to executable: %s", application_path
            )
        else:
            application_path = None
            _LOGGER.debug("Running in a normal Python process")
        return application_path

    def set_up_menu(self):
        """Set up system tray menu."""
        self.app.icon = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../resources/statusbar-grey.png")
        )
        start_at_login_menu_item = rumps.MenuItem(
            title="Start at login", callback=self.toggle_start_at_login
        )
        start_at_login_menu_item.state = self.start_at_login
        self.app.menu = [
            rumps.MenuItem(title="Settings...", callback=self.settings),
            start_at_login_menu_item,
            rumps.MenuItem(title="About...", callback=self.about),
            rumps.MenuItem(title="Help", callback=self.help),
        ]

    def start_system_tray_app(self):
        """Start system tray application."""
        self.app.run()

    def settings(self, sender):
        """Show settings dialogue."""
        webhook_uri = self.webhook_uri if self.webhook_uri else WEBHOOK_URI_SAMPLE
        settings_window = rumps.Window(
            "Enter the Webhook URL here", "Settings", webhook_uri, dimensions=(640, 20)
        )
        response = settings_window.run()
        if response.clicked:
            text_entered = str(response.text)
            _LOGGER.debug("URL entered: %s", text_entered)
            self.webhook_uri = text_entered
            if text_entered != WEBHOOK_URI_SAMPLE:
                self._configuration[CONFIGURATION_WEBHOOK_URI] = text_entered
                self.write_configuration()

    def about(self, sender):
        """Show about dialogue."""
        rumps.alert(
            "About",
            f"{APPLICATION_NAME} for Home Assistant.\nVersion: {__version__}",
        )

    def help(self, sender):
        """Open help."""
        webbrowser.open(APPLICATION_HOMEPAGE, new=2)

    def toggle_start_at_login(self, sender):
        """Choose whether to start the app at login or not."""
        self.start_at_login = not sender.state
        sender.state = self.start_at_login

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
        # Outer loop is ensuring that the application is reconnecting to Teams if the connection is completely lost.
        while True:
            uri = f"ws://{WEBSOCKET_HOSTNAME}:{WEBSOCKET_PORT}?token={self.token}&protocol-version=2.0.0&manufacturer={WEBSOCKET_MANUFACTURER}&device=Mac&app={WEBSOCKET_APPLICATION_NAME}&app-version={WEBSOCKET_APPLICATION_VERSION}"
            try:
                async with websockets.connect(uri) as websocket:
                    _LOGGER.debug("Websocket connection opened: %s", uri)
                    # Inner loop is ensuring that the websocket connection is opened once and kept open.
                    self.websocket_connected = True
                    try:
                        while True:
                            _LOGGER.debug(
                                "Pairing request pending: %s",
                                self.websocket_pairing_request_pending,
                            )
                            if (
                                not self.token
                                and self._websocket_can_pair
                                and not self.websocket_pairing_request_pending
                            ):
                                _LOGGER.debug("Sending pairing request")
                                self.websocket_pairing_request_pending = True
                                await websocket.send(
                                    '{"action":"pair","parameters":{},"requestId":1}'
                                )
                            # Reading messages from websocket.
                            message: str | bytes = await websocket.recv()
                            _LOGGER.debug("Received message: %s", message)
                            await self.process_message(message)
                    except websockets.exceptions.ConnectionClosedOK as exc:
                        _LOGGER.debug("Websocket connection closed ok: %s", exc)
                        self.websocket_pairing_request_pending = False
                    except websockets.exceptions.ConnectionClosedError as exc:
                        _LOGGER.debug("Websocket connection closed error: %s", exc)
                        self.websocket_pairing_request_pending = False
            except OSError as exc:  # noqa: PERF203
                _LOGGER.debug("Websocket connection failed: %s", exc)
                self.websocket_connected = False
                self.websocket_pairing_request_pending = False
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
                    await self.process_token_refresh(
                        decoded_message[TEAMS_MESSAGE_TOKEN_REFRESH]
                    )
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
        # Check if re-pairing information is available.
        if (
            "meetingPermissions" in meeting_update["meetingUpdate"]
            and "canPair" in meeting_update["meetingUpdate"]["meetingPermissions"]
        ):
            if bool(meeting_update["meetingUpdate"]["meetingPermissions"]["canPair"]):
                self._websocket_can_pair = True
                _LOGGER.info("Re-pairing required")
                self.token = ""
                self.websocket_paired = False
            else:
                self._websocket_can_pair = False
                # Assume we are paired if the meeting permissions say that we can't pair AND we have a token.
                self.websocket_paired = self.token
        # Don't send the same message payload twice in a row within 30 seconds.
        if (
            MEETING_UPDATE_LAST_MESSAGE in self._meeting_update_cache
            and self._meeting_update_cache[MEETING_UPDATE_LAST_MESSAGE]
            == meeting_update
        ):
            _LOGGER.debug(
                "Ignoring meeting update because it is the same information already sent within the last %s seconds",
                MEETING_UPDATE_SEND_BACKOFF_IN_SECONDS,
            )
        elif self.webhook_uri:
            # Home Assistant expects:
            # * Method: PUT
            # * Content-Type: application/json
            # * JSON encoded payload
            try:
                with httpx.Client() as client:
                    headers = {"Content-Type": "application/json"}
                    response = client.put(
                        self.webhook_uri, headers=headers, json=meeting_update
                    )
                    _LOGGER.debug("Webhook response: %s", response)
                    # Update cache
                    self._meeting_update_cache[MEETING_UPDATE_LAST_MESSAGE] = (
                        meeting_update
                    )
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
                        yaml = YAML(typ="safe")
                        configuration = yaml.load(stream)
                        self._configuration = configuration if configuration else {}
                    except YAMLError as exc:
                        _LOGGER.warning("Unable to read configuration: %s", exc)
        except OSError as error:
            _LOGGER.warning("Unable to read configuration from file: %s", error)

    def write_configuration(self):
        """Write configuration to file."""
        try:
            with open(self.configuration_file, mode="w") as stream:
                yaml = YAML(typ="safe")
                yaml.default_flow_style = False
                yaml.dump(self._configuration, stream)
        except OSError as error:
            _LOGGER.warning("Unable to write configuration to file: %s", error)
