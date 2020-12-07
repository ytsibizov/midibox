"""led - LED state enumeration."""

from enum import Enum


class Led(Enum):
    """LED state, either On or Off (blinking is not supported / used)."""

    On = 1
    Off = 2
