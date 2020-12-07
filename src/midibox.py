"""midibox - a simple layer to allow MIDI controllers to control Positive Grid Spark amplifier."""

import logging
import time
from enum import Enum
from typing import List, Optional

import bluetooth
import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

from spark import BluetoothInterface
from controller.led import Led
from controller.icon import IconGBoard
from controller.xtouch import BehringerXTouchMini

# Hex Code Spark Tone Commands
TONE1 = '01 38 00 00 00'  # SET PRESET INT 0x## 0x##
TONE2 = '01 38 00 00 01'
TONE3 = '01 38 00 00 02'
TONE4 = '01 38 00 00 03'
TONE_CMD_LIST = [TONE1, TONE2, TONE3, TONE4]

CONFIG1 = '02 01 00 00 00'  # GET CONFIG INT 0x## 0x##
CONFIG2 = '02 01 00 00 01'
CONFIG3 = '02 01 00 00 02'
CONFIG4 = '02 01 00 00 03'
CONFIG_CMD_LIST = [CONFIG1, CONFIG2, CONFIG3, CONFIG4]

HW_NAME = '02 11'  # GET NAME
HW_ID = '02 23'  # GET ID
CURRENT_CONFIG = '02 10'  # GET CURRENT_PRESET

# 0-based, buttons are 0..7
BUTTON_ONOFF = 0
BUTTON_PRESET0 = 4

NUM_PRESETS = 4
NUM_BUTTONS = 8

def reconnect(bt):
    """Reconnect Bluetooth."""
    logging.debug('Amp ID')
    bt.send(HW_NAME)
    bt.receive()
    logging.debug('Amp SN')
    bt.send(HW_ID)
    bt.receive()
    logging.debug('Amp Presets')
    for slot in range(0, 4):
        logging.debug('Preset {0}'.format(slot))
        bt.send(CONFIG_CMD_LIST[slot])
        bt.receive()
    logging.debug('Current preset:')
    bt.send(CURRENT_CONFIG)
    messages = bt.receive()
    preset = None
    if len(messages) == 1:
        preset = int.from_bytes(messages[0][-3:-1], 'big')
    return preset


def tone_control_loop(midi: MidiInterface) -> None:
    """Main amp control loop using MIDI interface."""
    midi.set_leds_midi_found()
    selected_slot = None
    bt = BluetoothInterface()
    spark_connected = False
    midi.set_leds_off(spark_connected)
    while True:
        button = midi.get_button()
        if button is None:
            time.sleep(0.1)
            continue
        if button == BUTTON_ONOFF:
            selected_slot = None
            if not spark_connected:
                logging.debug('scan')
                midi.set_leds_scan()
                if bt.scan():
                    logging.debug('connect')
                    bt.connect()
                    selected_slot = reconnect(bt)
                    spark_connected = True
            else:
                logging.debug('disconnect')
                bt.disconnect()
                spark_connected = False
            midi.set_leds_off(spark_connected)
            if selected_slot is not None:
                midi.set_preset_led(selected_slot)
        if spark_connected and button in range(BUTTON_PRESET0, BUTTON_PRESET0+NUM_PRESETS):
            selected_slot = button - BUTTON_PRESET0
            try:
                bt.send(TONE_CMD_LIST[selected_slot])
                midi.set_preset_led(selected_slot)
                bt.receive()
            except bluetooth.btcommon.BluetoothError:
                logging.info('BT connection lost')
                bt.disconnect()
                spark_connected = False
                midi.set_leds_off(spark_connected)
        time.sleep(0.1)


def midibox():
    """Midibox application."""
    logging.basicConfig(level=logging.DEBUG)
    midi = None
    while midi is None:
        try:
            midi = BehringerXTouchMini()
        except NoMidiDeviceException:
            logging.debug('No Behringer MIDI')
        try:
            midi = IconGBoard()
        except NoMidiDeviceException:
            logging.debug('No Icon MIDI')
        if midi is None:
            logging.debug('No MIDI, sleep 10 seconds')
            time.sleep(10)
    logging.debug('Draining MIDI queue....')
    while midi.get_button() is not None:
        pass  # drain MIDI messages
    tone_control_loop(midi)


# Start 'main' logic
if __name__ == '__main__':
    midibox()
