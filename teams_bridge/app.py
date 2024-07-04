"""Teams bridge application."""
import logging

from .teams_bridge import TeamsBridge
from .__version__ import __version__


def main():
    """Execute command line tool."""
    # Set up logger
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info(f"Teams Bridge (version {__version__})...")
    app = TeamsBridge()
    app.run()


if __name__ == "__main__":
    main()
