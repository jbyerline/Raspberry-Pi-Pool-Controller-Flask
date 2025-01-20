import utils

logger = utils.logger

class MockGPIO:
    BCM = "BCM"
    OUT = "OUT"

    @staticmethod
    def setmode(mode):
        logger.info(f"Mock: Set mode {mode}")

    @staticmethod
    def setup(pin, mode):
        logger.info(f"Mock: Setup pin {pin} as {mode}")

    @staticmethod
    def output(pin, state):
        logger.info(f"Mock: Setting pin {pin} to {'HIGH' if state else 'LOW'}")

# Replace RPi.GPIO with the mock if unavailable
try:
    import RPi.GPIO as GPIO
except ImportError:
    logger.warning("RPi.GPIO not available. Using MockGPIO.")
    GPIO = MockGPIO()
