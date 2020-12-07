"""xtouch -- support for Behring X-Touch Mini MIDI controller."""

import logging

from generic import MidiInterface
from led import Led
from rtmidi.midiconstants import NOTE_ON


class BehringerXTouchMini(MidiInterface):
    """Behringer X-Touch Mini MIDI controller. It is not a footswitch."""

    def __init__(self):
        """Initialize the class and try to find hardware."""
        self.device_name = 'X-TOUCH MINI'
        self.init()

    def get_button(self):
        """Get a MIDI message, convert to button (0-7), top row (0-3) to select preset."""
        button = None
        msg = self.indev.get_message()
        if msg:
            message, deltatime = msg
            logging.debug('MIDI IN: %r' % (message))
            if message[0] == 138 and message[2] == 0:
                button = message[1] - 8
                if (button >= 0) and (button <= 8):
                    logging.debug('Button {0}'.format(button))
                    return button
                if button is not None:
                    logging.debug('Button {0}'.format(button))
                    return button
        return None

    def set_led(self, led: int, mode: Led):
        """Set LED."""
        if led not in range(0, 8):
            return None
        if mode == Led.On:
            velocity = 1
        else:
            velocity = 0
        msg = [NOTE_ON, led, velocity]
        self.outdev.send_message(msg)
        return None
