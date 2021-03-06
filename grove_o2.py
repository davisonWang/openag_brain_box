"""
This module consists of code for interacting with a Grove O2 sensor.
"""

import serial
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/home/pi/openag_brain_box/ui/main.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GroveO2:
    """
    Class that represents a Grove O2 sensor instance and provides functions
    for interfacing with the sensor.
    """

    def __init__(self, analog_port=0, serial_port='/dev/serial/by-id/usb-Numato_Systems_Pvt._Ltd._Numato_Lab_8_Channel_USB_GPIO_Module-if00', pseudo=False):
        self.analog_port = analog_port
        self.serial_port = serial_port
        self.pseudo = pseudo
        self.o2 = None
        self.sensor_is_connected = True
        self.connect()

    def connect(self):
        if self.pseudo:
            logger.info('Connected to pseudo sensor')
            return
        try:
            self.serial = serial.Serial(self.serial_port, 19200, timeout=1)
            logger.debug("self.serial.isOpen() = {}".format(self.serial.isOpen()))
            if not self.sensor_is_connected:
                self.sensor_is_connected = True
                logger.info('Connected to sensor')
        except:
            if self.sensor_is_connected:
                self.sensor_is_connected = False
                logger.warning('Unable to connect to sensor')

    def poll(self):
        if self.pseudo:
            self.o2 = 19.3
            return
        if self.sensor_is_connected:
            try:
                self.serial.write(('adc read {}\r'.format(self.analog_port)).encode())
                response = self.serial.read(25)
                voltage = float(response[10:-3]) * 5 / 1024
                o2 = voltage * 0.21 / 2.0 * 100 # percent
                logger.debug('o2 = {}'.format(o2))
            except:
                self.o2 = None
                self.sensor_is_connected = False
        else:
            self.connect()

    def transmitToConsole(self, id='O2'):
        if self.o2 is not None:
            print(id, ': ', self.o2, '%')

    def transmitToMemcache(self, memcache_shared, id='o2'):
        if self.o2 is not None:
            memcache_shared.set(id, '{0:.1f}'.format(self.o2))
