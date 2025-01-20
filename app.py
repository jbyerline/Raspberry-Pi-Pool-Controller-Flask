import os
import sys
import datetime
import logging
from flask import Flask, render_template, jsonify
import utils
from lib.hardwareController import HardwareController
from lib.temperatureController import TemperatureController
from lib.poolLightController import PoolLightController
from lib.waterfallController import WaterfallController
from lib.poolPumpController import PoolPumpController


class IgnoreRootEndpointFilter(logging.Filter):
    def filter(self, record):
        # Ignore GET requests to the root endpoint
        invalid_strings = ["GET / ", "HEAD / ", "GET /static", "GET /favicon", "GET /apple"]
        return not any(s in record.getMessage() for s in invalid_strings)

logging.getLogger('werkzeug').addFilter(IgnoreRootEndpointFilter())

logger = utils.logger
app = Flask(__name__)

# Auto-enable mock mode if running on macOS or Windows
USE_MOCK = sys.platform != "linux"

# Initialize hardware controllers
hardware = HardwareController(use_mock=USE_MOCK)
temperature = TemperatureController(use_mock=USE_MOCK)
pool_lights = PoolLightController(hardware)
waterfall = WaterfallController(hardware)
pool_pump = PoolPumpController(hardware)

@app.route("/")
def index():
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    app_version = os.getenv("APP_VERSION", "Unknown")
    return render_template('index.html', year=year, version=app_version)

@app.route("/<device>/<action>")
def control_device(device, action):
    if device == "poolLight":
        pool_lights.toggle(action)
        return jsonify({"poolLightStatus": pool_lights.get_status()})
    elif device == "waterfall":
        waterfall.toggle(action)
        return jsonify({"waterfallStatus": waterfall.get_status()})
    elif device == "pump":
        pool_pump.toggle(action)
        return jsonify({"poolPumpStatus": action})
    return jsonify({"error": "Invalid device"}), 400

@app.route("/poolLight/status")
def get_pool_light_status():
    return jsonify({"poolLightStatus": pool_lights.get_status()})

@app.route("/waterfall/status")
def get_waterfall_status():
    return jsonify({"waterfallStatus": waterfall.get_status()})

@app.route("/airTemp")
def get_air_temp():
    temp = temperature.read_temperature("outdoor")
    return jsonify({"outdoorTemp": temp})

@app.route("/poolTemp")
def get_pool_temp():
    temp = temperature.read_temperature("pool")
    return jsonify({"poolTemp": temp})

if __name__ == '__main__':
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))
