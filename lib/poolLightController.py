import utils

logger = utils.logger

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    from lib.mock_gpio import GPIO  # ✅ Use mock if running locally
    RPI_AVAILABLE = False

class PoolLightController:
    def __init__(self, hardware, arduino_pin=2, gpio_pin=26, use_gpio=False):
        """
        Controls the pool lights using:
        - Arduino digital pin (5V) via pyFirmata
        - Raspberry Pi GPIO pin (3.3V) if `use_gpio=True`
        """
        self.hardware = hardware
        self.arduino_pin = arduino_pin
        self.gpio_pin = gpio_pin
        self.use_gpio = use_gpio and RPI_AVAILABLE  # Only enable GPIO if running on Raspberry Pi
        self.status = "off"

        if self.use_gpio:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(self.gpio_pin, GPIO.OUT)
                logger.info(f"Initialized GPIO pin {self.gpio_pin} for Pool Lights")
            except Exception as e:
                logger.error(f"Failed to initialize GPIO: {e}")
                self.use_gpio = False  # Fallback to Arduino if GPIO setup fails

    def toggle(self, action):
        """
        Toggles the pool light on/off.
        """
        if action not in ["on", "off"]:
            logger.warning(f"Invalid action: {action}")
            return

        self.status = action
        logger.info(f"Pool Lights {action.upper()}")

        try:
            if self.use_gpio:
                GPIO.output(self.gpio_pin, GPIO.HIGH if action == "on" else GPIO.LOW)
            else:
                self.hardware.board.digital[self.arduino_pin].write(1 if action == "on" else 0)
        except Exception as e:
            logger.error(f"Error controlling Pool Lights: {e}")

    def get_status(self):
        return self.status
