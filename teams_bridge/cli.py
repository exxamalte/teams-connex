"""Command-line tool."""
import logging
import asyncio
import threading
import time

import rumps
import websockets

from teams_bridge.__version__ import __version__


class TeamsBridge:
    """Teams bridge application."""

    def __init__(self):
        self.config = {
            "app_name": "Teams Bridge"
        }
        self.app = rumps.App(self.config["app_name"])
        self.set_up_menu()

    def set_up_menu(self):
        self.app.title = "🥷"

    def start_system_tray_app(self):
        # self.app = rumps.App('VPN', quit_button=None)
        # self.app.menu = [
        #     rumps.MenuItem('Quit', callback=self.disconnect_vpn),
        # ]
        self.app.run()

    def start_updater_thread(self):
        token = ""
        url = f"ws://localhost:8124?token={token}&protocol-version=2.0.0&manufacturer=SubspaceSoftware&device=Mac&app=TeamsBridge&app-version=2.0.26"
        websocket_thread = threading.Thread(target=self.start_websocket_thread)
        websocket_thread.start()

    def start_websocket_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.websocket_handler())

    async def websocket_handler(self):
        token = ""
        uri = f"ws://localhost:8124?token={token}&protocol-version=2.0.0&manufacturer=SubspaceSoftware&device=Mac&app=TeamsBridge&app-version=2.0.26"

        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    await websocket.send("{\"action\":\"pair\",\"parameters\":{},\"requestId\":1}")

                    # Your WebSocket logic here
                    message = await websocket.recv()
                    print(f"Received message: {message}")

                    # Handle token refresh
                    # Example: {"tokenRefresh":"1273d305-d1a5-4484-b623-a65467a72a50"}

                    # Handle meeting update
                    # Example: {"meetingUpdate":{"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}
                    # Example: {"meetingUpdate":{"meetingState":{"isMuted":false,"isVideoOn":false,"isHandRaised":false,"isInMeeting":false,"isRecordingOn":false,"isBackgroundBlurred":false,"isSharing":false,"hasUnreadMessages":false},"meetingPermissions":{"canToggleMute":false,"canToggleVideo":false,"canToggleHand":false,"canToggleBlur":false,"canLeave":false,"canReact":false,"canToggleShareTray":false,"canToggleChat":false,"canStopSharing":false,"canPair":false}}}

                    time.sleep(2.0)
                except websockets.exceptions.ConnectionClosedError:
                    pass

    def run(self):
        self.start_updater_thread()
        self.start_system_tray_app()


def main():
    """Execute command line tool."""
    # Set up logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Teams Bridge (version {__version__})...")
    app = TeamsBridge()
    app.run()


if __name__ == "__main__":
    # asyncio.run(main())
    main()
