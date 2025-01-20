import utils

logger = utils.logger

class MockFirmata:
    def __init__(self, port):
        logger.info(f"Mock: Pretending to connect to Arduino at {port}")
        self.digital_pins = {}

    def digital_write(self, pin, value):
        self.digital_pins[pin] = value
        logger.info(f"Mock: Writing {value} to digital pin {pin}")

    def get_pin(self, pin_config):
        logger.info(f"Mock: Getting fake pin {pin_config}")
        return MockPin()

    def exit(self):
        logger.info("Mock: Closing fake Arduino connection")

    def __del__(self):
        logger.info("Mock: Deleting fake Arduino object")

class MockPin:
    def read(self):
        return 0.5  # Simulate a stable voltage reading

    def write(self, value):
        logger.info(f"Mock: Writing {value} to a fake pin")
