import lib.tempuratureController
gaction = "0"

def waterfall(action):
    global gaction

    if action == 'off':
        gaction = "0"
        print("Waterfall off")
        off()


    elif action == 'on':
        gaction = "1"
        print("Waterfall on")
        on()

# def waterfallSchedule():
#     now = datetime.datetime.now()
#     timeString = int(now.strftime("%H"))
#
#     if(timeString >= 17 and timeString <= 18):
#         print("Current Hour - ", timeString)
#         print("Waterfall on (SCHEDULED)")
#         on()
#     elif(gaction == 'OFF'):
#         off()

def on():
    lib.tempuratureController.board.digital[3].write(1)

def off():
    lib.tempuratureController.board.digital[3].write(0)

def getWaterStatus():
    return gaction
