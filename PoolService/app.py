import datetime
import pymysql.cursors
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from DBUtils.PersistentDB import PersistentDB
from lib.tempuratureController import tempSetUp, outdoorTemp, poolTemp
from lib.poolLightController import poolLights
from lib.waterfallController import waterfall, waterfallSchedule
from lib.poolPumpController import poolPump


app = Flask(__name__)


def connect_db():
    return PersistentDB(
        creator = pymysql, host='192.168.7.251',
        user='root', password='[PASSWORD]',
        db='test', autocommit=True, charset='utf8mb4',
        cursorclass = pymysql.cursors.DictCursor)

def get_db():
    '''Opens a new database connection per app.'''

    if not hasattr(app, 'db'):
        app.db = connect_db()
    return app.db.connection()

def create_table():
    print("Creating Table")
    cursor = get_db().cursor()
    insert_query = (
        "CREATE TABLE IF NOT EXISTS poolDataTable"
        "(id int AUTO_INCREMENT PRIMARY KEY, poolTemp float, airTemp float, solarTemp float, dateTime datetime)"
    )
    cursor.execute(insert_query)


def add_record():
    now = datetime.datetime.now()
    timeString = int(now.strftime("%H%M%S"))
    # print("Time: ", timeString)
    if (timeString == 70000 or timeString == 120000  or timeString == 190000):
        print("Adding Temperatures to DB")
        cursor = get_db().cursor()
        insert_query = (
            "INSERT INTO poolDataTable "
            "(poolTemp, airTemp, solarTemp, dateTime) "
            "VALUES "
            "(%s, %s, %s, %s);"
        )
        values = [poolTemp(), outdoorTemp(), outdoorTemp(), now]

        cursor.execute(insert_query, values)

# create DB table if it doesnt already exist
create_table()

# set up Arduino board
tempSetUp()

# Scheduler object
sched = BackgroundScheduler()

# add your job here
sched.add_job(waterfallSchedule, 'interval', seconds=5, misfire_grace_time=3600)
sched.add_job(add_record, 'interval', seconds=1, misfire_grace_time=3600)

# start job
sched.start()

@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%a %m-%d-%Y")
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

@app.route("/airTemp")
def getAirTemp():
    return outdoorTemp()

@app.route("/poolTemp")
def getPoolTemp():
    return poolTemp()


if __name__ == '__main__':
    app.run(host='192.168.7.25', port=8000, debug=False)

