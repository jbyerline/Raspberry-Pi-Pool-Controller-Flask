import RPi.GPIO as GPIO
import lib.tempuratureController

def poolPump(action):

    pinNumber = 14
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pinNumber, GPIO.OUT)

    if action == 'off':
        print("Pool Pump off")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[4].write(0)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.LOW)

    elif action == 'on':
        print("Pool Pump on")
        # For using Arduino IO 5v
        lib.tempuratureController.board.digital[4].write(1)

        # For using onboard GPIO 3.3v
        # GPIO.output(pinNumber, GPIO.HIGH)


