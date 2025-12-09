import os
import sys
import datetime
import logging
import warnings

import schedule
import atexit
import time
from threading import Thread
from flask import Flask, render_template, jsonify, request
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

@app.route("/temperature-data", methods=["GET"])
def get_temperature_data():
    try:
        # Get time range and granularity from query params
        time_range = request.args.get("range", "7d")  # default to last 7 days
        granularity = request.args.get("granularity", "hourly")

        # Determine the start date based on time range
        now = datetime.datetime.now()
        if time_range.endswith("h"):
            start_date = now - datetime.timedelta(hours=int(time_range[:-1]))
        elif time_range.endswith("d"):
            start_date = now - datetime.timedelta(days=int(time_range[:-1]))
        elif time_range.endswith("w"):
            start_date = now - datetime.timedelta(weeks=int(time_range[:-1]))
        else:
            return jsonify({"error": "Invalid time range"}), 400

        # Define aggregation pipeline for granularity
        if granularity == "hourly":
            group_time = {"year": {"$year": "$date"}, "month": {"$month": "$date"}, "day": {"$dayOfMonth": "$date"}, "hour": {"$hour": "$date"}}
        elif granularity == "daily":
            group_time = {"year": {"$year": "$date"}, "month": {"$month": "$date"}, "day": {"$dayOfMonth": "$date"}}
        elif granularity == "weekly":
            group_time = {"year": {"$year": "$date"}, "week": {"$week": "$date"}}
        else:
            return jsonify({"error": "Invalid granularity"}), 400

        pipeline = [
            {"$match": {"date": {"$gte": start_date}}},
            {"$group": {
                "_id": group_time,
                "avg_air_temp": {"$avg": "$air_temp"},
                "avg_water_temp": {"$avg": "$water_temp"},
            }},
            {"$sort": {"_id": 1}}
        ]

        data = list(collection.aggregate(pipeline))

        # Format response
        result = []
        for entry in data:
            result.append({
                "date": entry["_id"],
                "air_temp": round(entry["avg_air_temp"], 2),
                "water_temp": round(entry["avg_water_temp"], 2)
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_last_valid_temps():
    """Fetch the most recent temps from Mongo, if any."""
    last = collection.find_one(sort=[("date", -1)])
    if not last:
        return None, None
    return last.get("air_temp"), last.get("water_temp")


def is_valid_temp(new_value, last_value, *, min_temp=20, max_temp=120, max_delta=None):
    """
    Basic anomaly check:
      - within absolute min/max range
      - not jumping more than max_delta from last_value (if provided)
    """
    if new_value is None:
        return False

    if new_value < min_temp or new_value > max_temp:
        return False

    if last_value is not None and max_delta is not None:
        if abs(new_value - last_value) > max_delta:
            return False

    return True

def log_temps():
    last_air, last_pool = get_last_valid_temps()

    outdoor_temp = temperature.read_temperature("outdoor")
    pool_temp = temperature.read_temperature("pool")

    # Example: air can swing faster than water
    air_ok = is_valid_temp(
        outdoor_temp,
        last_air,
        min_temp=20,
        max_temp=120,
        max_delta=15,   # max 15°F change per logging interval
    )

    pool_ok = is_valid_temp(
        pool_temp,
        last_pool,
        min_temp=30,
        max_temp=100,
        max_delta=5,    # pool water is slow to change; 5°F jump is suspect
    )

    if not air_ok:
        logger.warning(
            "Anomalous outdoor temp %.2f°F (last=%.2f°F); skipping log",
            outdoor_temp, (last_air if last_air is not None else float("nan"))
        )
        outdoor_temp = None  # or use last_air if you prefer to "hold" the value

    if not pool_ok:
        logger.warning(
            "Anomalous pool temp %.2f°F (last=%.2f°F); skipping log",
            pool_temp, (last_pool if last_pool is not None else float("nan"))
        )
        pool_temp = None  # or use last_pool

    # If both are bad, skip this tick entirely
    if outdoor_temp is None and pool_temp is None:
        logger.error("No valid temperatures to log; skipping Mongo insert")
        return

    # If one is bad but the other is fine, you can:
    # - skip logging both, or
    # - log the good one and reuse last good for the bad one.
    # Example here: reuse last good value if needed:
    if outdoor_temp is None:
        outdoor_temp = last_air
    if pool_temp is None:
        pool_temp = last_pool

    collection.insert_one({
        "date": datetime.datetime.now(),
        "air_temp": outdoor_temp,
        "water_temp": pool_temp,
    })

    logger.info(
        "Logged temperatures: %s°F (Outdoor), %s°F (Pool) to Mongo DB",
        outdoor_temp, pool_temp
    )

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

    port = (os.getenv("PORT", "8000"))

    NGROK_ENABLED = utils.str_to_bool(os.getenv("NGROK_ENABLED", "false"))
    logger.info(f"NGROK_ENABLED: {NGROK_ENABLED}")
    # If ngrok is enabled
    if NGROK_ENABLED:
        logger.info("Starting ngrok tunnel...")
        # Start ngrok in a separate thread
        ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))
        public_url = ngrok.connect(port, domain=os.getenv("NGROK_DOMAIN")).public_url
        logger.info(f"ngrok tunnel opened: {public_url}")

        # Shut down ngrok when exiting the app
        atexit.register(lambda: ngrok.disconnect(public_url))

    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(port))
