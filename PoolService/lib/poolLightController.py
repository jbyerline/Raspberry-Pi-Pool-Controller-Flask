import RPi.GPIO as GPIO
import lib.tempuratureController

status = '0'


def poolLights(action):
    pinNumber = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pinNumber, GPIO.OUT)

    global status

    if action == 'off':
        status = '0'
        print("Pool Lights off")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[2].write(0)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.LOW)

    elif action == 'on':
        status = '1'
        print("Pool Lights on")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[2].write(1)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.HIGH)


def getLightStatus():
    return status
