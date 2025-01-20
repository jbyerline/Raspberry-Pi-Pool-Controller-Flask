import math
import time
from lib.hardwareController import pyfirmata2
import utils

logger = utils.logger

class TemperatureController:
    def __init__(self, arduino_port="/dev/ttyUSB0", use_mock=False):
        self.use_mock = use_mock
        self.board = None
        self.pin_voltage = 5.0
        self.analog_pins = {}

        if self.use_mock:
            logger.info("Using Mock TemperatureController")
            self.board = pyfirmata2.Arduino("mock")
        else:
            self._initialize_arduino(arduino_port)

    def _initialize_arduino(self, arduino_port):
        """Attempts to initialize connection with Arduino."""
        try:
            self.board = pyfirmata2.Arduino(arduino_port)
            logger.info("Connected to Arduino at %s", arduino_port)

            # Start iterator (important for reading analog input updates)
            it = pyfirmata2.util.Iterator(self.board)
            it.start()

            # Initialize analog pins
            self.analog_pins["outdoor"] = self.board.get_pin('a:0:i')
            self.analog_pins["pool"] = self.board.get_pin('a:1:i')

            logger.info("Temperature sensors initialized.")

        except Exception as e:
            logger.error("Failed to connect to Arduino: %s", str(e))
            self.use_mock = True
            self.board = pyfirmata2.Arduino("mock")

    def read_temperature(self, sensor="outdoor", retries=3, delay=0.5):
        """
        Reads the current temperature value from the specified sensor.
        Retries if necessary to ensure a valid reading.
        """
        if self.use_mock:
            return 75.0 if sensor == "outdoor" else 78.0  # Mock values

        if sensor not in self.analog_pins:
            logger.error("Invalid sensor name: %s", sensor)
            return None

        for attempt in range(retries):
            raw_value = self.analog_pins[sensor].read()
            if raw_value is not None:
                temp = self._convert_voltage_to_temperature(raw_value)
                logger.info("Temperature reading from %s: %.2f°F", sensor, temp)
                return temp

            logger.warning("No data from sensor: %s (attempt %d/%d)", sensor, attempt + 1, retries)
            time.sleep(delay)

        logger.error("Failed to get a valid reading from sensor: %s after %d attempts", sensor, retries)
        return None

    def _convert_voltage_to_temperature(self, volt):
        """
        Converts the voltage reading from the thermistor to temperature in Fahrenheit
        using the Steinhart-Hart equation.
        """
        try:
            thermistor_adc_val = volt * 1023
            output_voltage = (thermistor_adc_val * self.pin_voltage) / 1023.0
            thermistor_resistance = ((5 * (10.0 / output_voltage)) - 10) * 1000
            therm_res_ln = math.log(thermistor_resistance)

            # **Steinhart-Hart Thermistor Equation:**
            A = 0.001129148
            B = 0.000234125
            C = 8.76741e-8

            temperature_kelvin = 1 / (A + (B * therm_res_ln) + (C * therm_res_ln ** 3))
            temperature_celsius = temperature_kelvin - 273.15
            temperature_fahrenheit = (temperature_celsius * 1.8) + 32

            return round(temperature_fahrenheit, 2)

        except Exception as e:
            logger.error("Error converting temperature: %s", str(e))
            return None
