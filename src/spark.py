"""spark - BT RFCOM interface for Positive Grid Spark amplifier."""

import logging
import time
from enum import Enum
from typing import List, Optional

import bluetooth
import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

# Set Connection Port Default
SERVER_PORT = 2


class BluetoothInterface(object):
    """Bluetooth connection to the Spark."""

    def __init__(self):
        """Initialize class but do not initiate connection."""
        self.spark_mac = None
        self.bt_socket = None

    def scan(self, duration=10) -> bool:
        """Scan for a BT device that is called "Spark"."""
        devices = bluetooth.discover_devices(duration, lookup_names=True)
        for addr, name in devices:
            if str(name).startswith('Spark'):
                logging.debug('Found {0} MAC {1}'.format(name, addr))
                self.spark_mac = addr
                return True
        return False

    def disconnect(self) -> None:
        """Disconnect Bluetooth."""
        try:
            self.bt_socket.close()
        except bluetooth.btcommon.BluetoothError:
            logging.debug('BT socket already closed')

    def connect(self) -> None:
        """Connect Bluetooth."""
        self.bt_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.bt_socket.connect((self.spark_mac, SERVER_PORT))

    def send_raw(self, command: str) -> None:
        """Send raw command."""
        command = str(command).replace(' ', '')
        logging.debug('Sending {0}'.format(command))
        msg = bytes.fromhex(command)
        self.bt_socket.send(msg)

    def send(self, command: str) -> None:
        """Send a command. The prefixes / suffixes are generated automatically."""
        command = str(command).replace(' ', '')
        logging.debug('Command {0}'.format(command))
        prefix = '01 fe 00 00 53 fe'.replace(' ', '')
        suffix1 = '00 00 00 00 00 00 00 00 00'.replace(' ', '')
        suffix2 = 'f0 01'.replace(' ', '')
        fake_seq = '01 01'.replace(' ', '')
        suffix = 'f7'.replace(' ', '')
        command_len = len(prefix)/2 + 1 + len(suffix1)/2 + len(suffix2)/2 + len(fake_seq)/2 + len(command)/2 + len(suffix)/2
        command_len = int(command_len)
        bt_command = prefix + ('%02x' % command_len) + suffix1 + suffix2 + fake_seq + command + suffix
        msg = bytes.fromhex(bt_command)
        self.bt_socket.send(msg)

    def receive(self) -> List[bytes]:
        """Receive a raw message from Spark."""
        last_message = False
        message: List[bytes]  = []
        while not last_message:
            data = self.bt_socket.recv(1024)
            if not data:
                return message
            last_message = (list(data)[-1] == 0xf7) and (len(data) < 0x6a)
            logging.debug('Received {0}'.format(bytes.hex(data)))
            message.append(data)
        return message
