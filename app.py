import os
import sys
import datetime
import logging
import warnings

import schedule
import atexit
import time
from threading import Thread
from flask import Flask, render_template, jsonify
from pyngrok import ngrok
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
warnings.filterwarnings("ignore", category=UserWarning, module="pyfirmata2")

logger = utils.logger

# MongoDB collections from utils
db = utils.db
collection = utils.collection
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

def log_temps():
    outdoor_temp = temperature.read_temperature("outdoor")
    pool_temp = temperature.read_temperature("pool")
    collection.insert_one({"date": datetime.datetime.now(), "air_temp": outdoor_temp, "water_temp": pool_temp})
    logger.info("Logged temperatures: %s°F (Outdoor), %s°F (Pool) to mongo DB", outdoor_temp, pool_temp)

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logger.error(f"Scheduler encountered an error: {e}")
        time.sleep(1)

if __name__ == '__main__':
    logger.info(f"Starting up {os.environ.get('SERVICE_NAME')} v{os.environ.get('APP_VERSION')}")

    # Schedule the job to run every n hours
    schedule.every(int(os.environ.get("LOG_TEMPS_EVERY_N_HOURS"))).hours.do(log_temps)

    # Start the scheduler in a separate thread to allow the app to continue running
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Start ngrok in a separate thread
    port = (os.getenv("PORT", "8000"))
    ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))
    public_url = ngrok.connect(port, domain=os.getenv("NGROK_DOMAIN")).public_url
    logger.info(f"ngrok tunnel opened: {public_url}")

    # Shut down ngrok when exiting the app
    atexit.register(lambda: ngrok.disconnect(public_url))

    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(port))
