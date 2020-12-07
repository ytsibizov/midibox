"""midibox - a simple layer to allow MIDI controllers to control Positive Grid Spark amplifier."""

import logging
import time
from typing import Optional

import rtmidi
from led import Led

# 0-based, buttons are 0..7
BUTTON_ONOFF = 0
BUTTON_PRESET0 = 4

NUM_PRESETS = 4
NUM_BUTTONS = 8


class NoMidiDeviceException(Exception):
    """Exception accessing MIDI device."""


class MidiInterface(object):
    """Generic MIDI Interface. Does nothing."""

    def __init__(self) -> None:
        """Initalize."""
        self.device_name: str
        self.midiin: rtmidi.MidiIn
        self.indev: rtmidi.MidiBase
        self.midiout: rtmidi.MidiOut
        self.outdev: rtmidi.MidiBase

    def init(self) -> None:
        self.midiin = rtmidi.MidiIn()
        self.indev = self.find_midi_in()
        self.midiout = rtmidi.MidiOut()
        self.outdev = self.find_midi_out()

    def find_midi_in(self) -> rtmidi.MidiBase:
        """Try to find MIDI input port."""
        if self.midiin is None:
            raise NoMidiDeviceException
        num_ports = self.midiin.get_port_count()
        for port in range(0, num_ports):
            if str(self.midiin.get_port_name(port)).startswith(self.device_name):
                logging.debug('MIDI IN: {0}'.format(self.midiin.get_port_name(port)))
                return self.midiin.open_port(port)
        raise NoMidiDeviceException

    def find_midi_out(self) -> rtmidi.MidiBase:
        """Try to find MIDI output port."""
        if self.midiout is None:
            raise NoMidiDeviceException
        num_ports = self.midiout.get_port_count()
        for port in range(0, num_ports):
            if str(self.midiin.get_port_name(port)).startswith(self.device_name):
                logging.debug('MIDI OUT: {0}'.format(self.midiout.get_port_name(port)))
                return self.midiout.open_port(port)
        raise NoMidiDeviceException

    def get_button(self) -> Optional[int]:
        """Get number of button (0-7) pressed on the controller."""
        return None

    def set_led(self, led: int, mode: Led) -> None:
        """Set LED on or off."""

    def set_leds_midi_found(self) -> None:
        """Indicate MIDI Found event."""
        for led in range(0, NUM_BUTTONS):
            self.set_led(led, Led.On)
        time.sleep(0.5)
        for led in range(0, NUM_BUTTONS):
            self.set_led(led, Led.Off)
        time.sleep(0.5)
        for led in range(0, NUM_BUTTONS):
            self.set_led(led, Led.On)
        time.sleep(0.5)
        for led in range(0, NUM_BUTTONS):
            self.set_led(led, Led.Off)

    def set_leds_scan(self) -> None:
        """Indicate BT Scan is started event."""
        for led in range(BUTTON_PRESET0, BUTTON_PRESET0+NUM_PRESETS):
            self.set_led(led, Led.On)
        self.set_led(BUTTON_ONOFF, Led.Off)

    def set_leds_off(self, spark_connected) -> None:
        """Set all LEDs to off, except connection indicator."""
        for led in range(BUTTON_PRESET0, BUTTON_PRESET0+NUM_PRESETS):
            self.set_led(led, Led.Off)
        if spark_connected:
            self.set_led(BUTTON_ONOFF, Led.On)
        else:
            self.set_led(BUTTON_ONOFF, Led.Off)

    def set_preset_led(self, slot: int) -> None:
        """Set slot LED to On."""
        logging.debug('Changed to slot {0}'.format(slot))
        for led in range(0, NUM_PRESETS):
            if led == slot:
                self.set_led(BUTTON_PRESET0+led, Led.On)
            else:
                self.set_led(BUTTON_PRESET0+led, Led.Off)
