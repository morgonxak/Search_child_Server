#!/usr/bin/sudo python3
from flask import Flask, render_template, request
#from flask_googlemaps import GoogleMaps, Map
import sqlite3
from datetime import datetime


app = Flask(__name__, template_folder="templates")

@app.route("/")
def mapview():
    with sqlite3.connect("/target1/Dima/bd") as conn:
        cursor = conn.cursor()
        for row in cursor.execute('SELECT id from GPS_table ORDER BY Name LIMIT 3'):
            print(row)

    # creating a map in the view

    # sndmap = Map(
    #     identifier="sndmap",
    #     lat=55.3514756,
    #     lng=86.0936228,
    #     style="height: 100%; width: 100%;margin-top: 100px;margin-bottom: 100px;",
    #     markers=[
    #       {
    #          'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
    #          'lat': 55.3514756,
    #          'lng': 86.0936228,
    #          'infobox': "<b>Hello World</b>"
    #       },
    #       {
    #          'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
    #          'lat': 55.3514756,
    #          'lng': 86.0936228,
    #          'infobox': "<b>Hello World from other place</b>"
    #       }
    #     ]
    # )
    # return render_template('example.html', sndmap=sndmap)

@app.route("/test", methods=["GET"])
def getGPS():
    '''
    Получает координаты с телефона и записывет в базу данных
    :return:
     #[18 / Aug / 2019 11: 38:05] "GET /test?lat=55.3514818&lon=86.0935871 HTTP/1.1"
     217.118.79.42 - -     "GET /test?id=123&lat=55.3516896&lon=86.0940981 HTTP/1.1" 500 -
    '''
    id_user = request.args.get("id")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    print(lat, lon, id_user)
    #id = 1256

    timeReqvest = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  #Определяем время прихода запроса

    # Вставляем данные в таблицу

    with sqlite3.connect("/home/dima/ServerPython/androindServerMap/bd") as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO GPS_table VALUES (?,?,?,?)", [(timeReqvest, lat, lon, id)])
        conn.commit()
    return lat, lon

if __name__ == "__main__":

    app.debug = True
    app.run(host='0.0.0.0', port=256)