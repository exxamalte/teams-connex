"""Define a version constant."""

from typing import Final

MAJOR_VERSION: Final = 2024
MINOR_VERSION: Final = 7
PATCH_VERSION: Final = "0b4"

__short_version__: Final = f"{MAJOR_VERSION}.{MINOR_VERSION}"
__version__: Final = f"{__short_version__}.{PATCH_VERSION}"
