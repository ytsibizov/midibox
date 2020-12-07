"""icon -- Icon G-Board support."""

import logging
from typing import Optional

from generic import MidiInterface
from led import Led
from rtmidi.midiconstants import NOTE_ON


class IconGBoard(MidiInterface):
    """Icon GBoard MIDI Interface."""

    def __init__(self) -> None:
        """Initialize and try to find the board."""
        self.device_name = 'iCON G_Boar'
        self.init()

    def get_button(self) -> Optional[int]:
        """Get a MIDI message, convert to button (0-7), top row (0-3) to select preset.

        Top row:
        DEBUG:root:[144, 91, 0]
        DEBUG:root:[144, 91, 127]
        DEBUG:root:[144, 92, 0]
        DEBUG:root:[144, 92, 127]
        DEBUG:root:[144, 93, 0]
        DEBUG:root:[144, 93, 127]
        DEBUG:root:[144, 94, 0]
        DEBUG:root:[144, 94, 127]
        Bottom row:
        DEBUG:root:[144, 86, 127]
        DEBUG:root:[144, 86, 0]
        DEBUG:root:[144, 95, 127]
        DEBUG:root:[144, 95, 0]
        DEBUG:root:[144, 48, 127]
        DEBUG:root:[144, 48, 0]
        DEBUG:root:[144, 49, 127]
        DEBUG:root:[144, 49, 0]
        """
        button = None
        msg = self.indev.get_message()
        if msg:
            message, deltatime = msg
            logging.debug('MIDI IN: %r' % (message))
            if message[0] == 144 and message[2] == 127:
                button = message[1] - 91
                if (button >= 0) and (button <= 3):
                    logging.debug('Button {0}'.format(button))
                    return button
                if message[1] == 86:
                    button = 4
                if message[1] == 95:
                    button = 5
                if message[1] == 48:
                    button = 6
                if message[1] == 49:
                    button = 7
                if button is not None:
                    logging.debug('Button {0}'.format(button))
                    return button
        return None

    def set_led(self, led: int, mode: Led):
        """Set the LED."""
        notes = [91, 92, 93, 94, 86, 95, 48, 49]
        if led not in range(0, 8):
            return None
        if mode == Led.On:
            velocity = 127
        else:
            velocity = 0
        msg = [NOTE_ON, notes[led], velocity]
        self.outdev.send_message(msg)
        return None
