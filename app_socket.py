#!/usr/bin/sudo python3
from flask import Flask, render_template, request, redirect
#from flask_googlemaps import GoogleMaps, Map
import sqlite3
from datetime import datetime


app = Flask(__name__, template_folder="templates")
#GoogleMaps(app, key="AIzaSyCNs0yf756N9ChNjv8qYX7ijtZgNE0FEsA")

@app.route("/")
def mapview():
    with sqlite3.connect("/target1/Dima/bd") as conn:
        cursor = conn.cursor()
        for row in cursor.execute('SELECT id from GPS_table ORDER BY Name LIMIT 3'):
            print(row)

def is_valid_topic(topic):
    if topic == "foo":
        return False
    else:
        return True

@app.route('/topic/<topic>')
def show_topic(topic):
    if is_valid_topic(topic):
        return '''The topic is %s''' % topic
    else:
        return "404 error INVALID TOPIC", 404

@app.route("/test", methods=["GET"])
def getGPS():
    '''
    Получает координаты с телефона и записывет в базу данных
    :return:
     #[18 / Aug / 2019 11: 38:05] "GET /test?lat=55.3514818&lon=86.0935871 HTTP/1.1"
    '''
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    #id = request.args.get("id")
    return redirect('topic/%s' % lat)

if __name__ == "__main__":

    app.debug = True
    app.run(host='0.0.0.0', port=257)