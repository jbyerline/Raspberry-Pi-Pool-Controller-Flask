import datetime
# import sys
# import pymysql.cursors
# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, json
# from jinja2 import Template
# from DBUtils.PersistentDB import PersistentDB
from lib.tempuratureController import tempSetUp, outdoorTemp, poolTemp
from lib.poolLightController import poolLights, getLightStatus
from lib.waterfallController import waterfall, getWaterStatus
from lib.poolPumpController import poolPump


app = Flask(__name__)

# def connect_db():
#     return PersistentDB(
#         creator = pymysql, host='192.168.7.250',
#         user='root', password='adiumDB',
#         db='poolData', autocommit=True, charset='utf8mb4',
#         cursorclass = pymysql.cursors.DictCursor)
#
# def get_db():
#     '''Opens a new database connection per app.'''
#
#     if not hasattr(app, 'db'):
#         app.db = connect_db()
#     return app.db.connection()
#
# def create_table():
#     global check
#     print("Creating Table")
#     try:
#         with get_db().cursor() as cursor:
#             insert_query = (
#                 "CREATE TABLE IF NOT EXISTS poolDataTable"
#                 "(id int AUTO_INCREMENT PRIMARY KEY, poolTemp float, airTemp float, solarTemp float, dateTime datetime)"
#             )
#             cursor.execute(insert_query)
#             check = True
#             print("Check: ", check)
#     except:
#         check = False
#         print("Database Not Found While Creating Table")
#         print("Check: ", check)
#
#
# def add_record():
#     now = datetime.datetime.now()
#     timeString = int(now.strftime("%H%M%S"))
#     if (timeString == 83000 or timeString == 120000 or timeString == 150000 or timeString == 190000):
#         if (check == True):
#             print("Adding Temperatures to DB")
#             try:
#                 with get_db().cursor() as cursor:
#                     #cursor = get_db().cursor()
#                     insert_query = (
#                         "INSERT INTO poolDataTable "
#                         "(poolTemp, airTemp, solarTemp, dateTime) "
#                         "VALUES "
#                         "(%s, %s, %s, %s);"
#                     )
#                     values = [poolTemp(), outdoorTemp(), outdoorTemp(), now]
#
#                     cursor.execute(insert_query, values)
#             except:
#                 print("Database Not Found While Adding Record")
#         else:
#             print("Check was false. Not adding Records")
#             print("Database Not Found While Adding Record")
#
# # create DB table if it doesnt already exist
# create_table()

# set up Arduino board
tempSetUp()
#
# # Scheduler object
# sched = BackgroundScheduler()
#
# # add your job here
# sched.add_job(waterfallSchedule, 'interval', seconds=5, misfire_grace_time=3600)
# sched.add_job(add_record, 'interval', seconds=1, misfire_grace_time=3600)
#
# # start job
# sched.start()

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

@app.route("/poolLight/status")
def getPoolLightStatus():
    return getLightStatus()

@app.route("/waterfall/status")
def getWaterfallStatus():
    return getWaterStatus()

# @app.route("/data")
# def getPoolTempData():
#     with get_db().cursor() as cursor:
#         cursor.execute("SELECT JSON_ARRAYAGG(json_object('id', id, 'poolTemp', poolTemp,'airTemp', airTemp, 'solarTemp', solarTemp, 'dateTime', dateTime)) FROM poolDataTable")
#         poolTempData = cursor.fetchall()
#         myString = str(poolTempData)
#         # remove from front
#         myString = myString[130:]
#         # # remove from back
#         myString = myString[:-3]
# #       print(myString, file=sys.stdout)
#         jsonData = json.loads(myString)
#
# #        for i in range(len(jsonData)):
# #            print(jsonData[i], file=sys.stdout)
# #        print("\n", file=sys.stdout)
#
#         print(jsonData, file=sys.stdout)
#         print("\n", file=sys.stdout)
#         templateData = {
#             'json': jsonData,
#         }
#         tmpl = Template('''
# <table>
#    {% for i in jsonData) %}
#    <tr><td>{{ i }}</td></tr>
#    {% endfor %}
# </table>
# ''')
#     return tmpl.render()
#     #return render_template(tmpl)


if __name__ == '__main__':
    app.run(host='10.0.0.60', port=8000, debug=False)

