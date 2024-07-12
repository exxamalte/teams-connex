"""Teams Connex application."""

import logging
import os

import platformdirs

from teams_connex.__version__ import __version__
from teams_connex.app import TeamsConnex
from teams_connex.consts import APPLICATION_NAME, APPLICATION_SHORTENED_NAME


def main():
    """Execute command line tool."""
    # Set up logger.
    logfile = os.path.join(
        platformdirs.user_log_dir(appname=APPLICATION_NAME, ensure_exists=True),
        f"{APPLICATION_SHORTENED_NAME}.log",
    )
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s:%(name)s:%(module)s:%(message)s",
        filename=logfile,
    )
    logger = logging.getLogger(__name__)
    logger.info("%s started (version %s)...", APPLICATION_NAME, __version__)
    # Start application.
    app = TeamsConnex()
    app.run()


if __name__ == "__main__":
    main()
