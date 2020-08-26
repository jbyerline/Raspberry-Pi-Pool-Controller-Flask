import datetime
import lib.tempuratureController
gaction = 'off'

def waterfall(action):
    global gaction

    if action == 'off':
        gaction = action
        print("Waterfall off")
        off()


    elif action == 'on':
        gaction = action
        print("Waterfall on")
        on()

def waterfallSchedule():
    now = datetime.datetime.now()
    timeString = int(now.strftime("%H"))

    if(timeString >= 17 and timeString <= 18):
        print("Current Hour - ", timeString)
        print("Waterfall on (SCHEDULED)")
        on()
    elif(gaction == 'off'):
        off()

def on():
    lib.tempuratureController.board.digital[3].write(1)

def off():
    lib.tempuratureController.board.digital[3].write(0)
