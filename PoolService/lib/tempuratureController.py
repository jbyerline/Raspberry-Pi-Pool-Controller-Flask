import pyfirmata2
import math


def tempSetUp():
    global board
    global analog_0, analog_1
    global arduinoPinVoltage
    board = pyfirmata2.Arduino('/dev/ttyUSB0')
    print("Setting up the connection to the board ...")
    it = pyfirmata2.util.Iterator(board)
    it.start()
    arduinoPinVoltage= 5.0
    analog_0 = board.get_pin('a:0:i')
    analog_1 = board.get_pin('a:1:i')
    board.analog[0].enable_reporting()
    board.analog[1].enable_reporting()

def outdoorTemp():
    volt = analog_0.read()
    formatted_float = 0.0
    if (str(volt) != "None"):
        thermistor_adc_val = volt * 1023
        output_voltage = ((thermistor_adc_val * arduinoPinVoltage) / 1023.0)
        thermistor_resistance = ((5 * (10.0 / output_voltage)) - 10)
        thermistor_resistance = thermistor_resistance * 1000
        therm_res_ln = math.log(thermistor_resistance)
        # /*  Steinhart-Hart Thermistor Equation: */
        # /*  Temperature in Kelvin = 1 / (A + B[ln(R)] + C[ln(R)]^3)   */
        # /*  where A = 0.001129148, B = 0.000234125 and C = 8.76741*10^-8  */
        temperature = (1 / (0.001129148 + (0.000234125 * therm_res_ln) + (
                0.0000000876741 * therm_res_ln * therm_res_ln * therm_res_ln)))
        temperature = temperature - 273.15
        temperature = (temperature * 1.8) + 32
        formatted_float = "{:.2f}".format(temperature)
        print("Outdoor Temp: ", formatted_float)

    outdoorT = str(formatted_float)
    return outdoorT

def poolTemp():
    volt = analog_1.read()
    formatted_float = 0.0
    if (str(volt) != "None"):
        thermistor_adc_val = volt * 1023
        output_voltage = ((thermistor_adc_val * arduinoPinVoltage) / 1023.0)
        thermistor_resistance = ((5 * (10.0 / output_voltage)) - 10)
        thermistor_resistance = thermistor_resistance * 1000
        therm_res_ln = math.log(thermistor_resistance)
        # /*  Steinhart-Hart Thermistor Equation: */
        # /*  Temperature in Kelvin = 1 / (A + B[ln(R)] + C[ln(R)]^3)   */
        # /*  where A = 0.001129148, B = 0.000234125 and C = 8.76741*10^-8  */
        temperature = (1 / (0.001129148 + (0.000234125 * therm_res_ln) + (
                0.0000000876741 * therm_res_ln * therm_res_ln * therm_res_ln)))
        temperature = temperature - 273.15
        temperature = (temperature * 1.8) + 32
        formatted_float = "{:.2f}".format(temperature)
        print("Pool Temp: ", formatted_float)

    poolT = str(formatted_float)
    return poolT