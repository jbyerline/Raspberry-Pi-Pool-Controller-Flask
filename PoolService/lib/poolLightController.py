import RPi.GPIO as GPIO
import lib.tempuratureController

def poolLights(action):
    pinNumber = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pinNumber, GPIO.OUT)

    if action == 'off':
        print("Pool Lights off")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[2].write(0)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.LOW)

    elif action == 'on':
        print("Pool Lights on")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[2].write(1)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.HIGH)

