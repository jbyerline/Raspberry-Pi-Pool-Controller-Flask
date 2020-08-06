import datetime
from flask import Flask, render_template
from lib.tempuratureController import tempSetUp, outdoorTemp, poolTemp
from lib.poolLightController import poolLights
from lib.waterfallController import waterfall
from lib.poolPumpController import poolPump

app = Flask(__name__)

tempSetUp()

@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%a %m %d %Y")
    templateData = {
        'time': timeString,
        'outdoorT': outdoorTemp(),
        'poolT': poolTemp()
    }
    return render_template('index.html', **templateData)


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    if(deviceName == 'poolLight'):
        templateData = {
            'poolLightStatus': poolLights(action),
        }
    elif (deviceName == 'waterfall'):
        templateData = {
            'waterfallStatus': waterfall(action),
        }
    elif (deviceName == 'pump'):
        templateData = {
            'poolPumpStatus': poolPump(action),
        }

    return render_template('index.html', **templateData)

if __name__ == '__main__':
    app.run(host='192.168.7.25', port=8000, debug=False)

