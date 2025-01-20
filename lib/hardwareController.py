import utils

logger = utils.logger

try:
    import RPi.GPIO as GPIO
    import pyfirmata2
    RPI_AVAILABLE = True
except ImportError:
    logger.warning("RPi.GPIO or pyfirmata2 not available. Running in mock mode.")
    from lib.mock_gpio import GPIO
    from lib.mock_firmata import MockFirmata
    pyfirmata2 = type("pyfirmata2", (object,), {"Arduino": MockFirmata})
    RPI_AVAILABLE = False

class HardwareController:
    def __init__(self, arduino_port="/dev/ttyUSB0", use_mock=False):
        self.use_mock = use_mock or not RPI_AVAILABLE
        self.board = None

        if self.use_mock:
            logger.info("Using Mock HardwareController")
            self.board = MockFirmata("mock")
        else:
            try:
                self.board = pyfirmata2.Arduino(arduino_port)
                logger.info("Connected to Arduino at %s", arduino_port)
            except Exception as e:
                logger.error("Failed to connect to Arduino: %s", str(e))
                self.use_mock = True
                self.board = MockFirmata("mock")

    def control_arduino_relay(self, pin, state):
        if self.use_mock:
            logger.info(f"Mock: Setting Arduino pin {pin} to {state}")
        else:
            self.board.digital[pin].write(1 if state == "on" else 0)
