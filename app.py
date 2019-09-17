#!/usr/bin/sudo python3
from flask import Flask, render_template, request, redirect
#from flask_googlemaps import GoogleMaps, Map
import sqlite3
from datetime import datetime
from moduls.modul_analitic import analitic, Point

config = {}

#Настройки
config['BD'] = r"/home/dima/ServerPython/androindServerMap/bd"

app = Flask(__name__, template_folder="templates")

# Слои для проверок
list_shp_oms = [r"/home/dima/ServerPython/androindServerMap/shp/water_line/water.shp"]
analitic_user = analitic(list_shp_oms)

@app.route("/gps", methods=["GET"])
def getGPS():
    '''
    Получает координаты с телефона и записывет в базу данных
    :return:
     #[18 / Aug / 2019 11: 38:05] "GET /test?lat=55.3514818&lon=86.0935871 HTTP/1.1"
     217.118.79.42 - -     "GET /gps?id=123&lat=55.3516896&lon=86.0940981 HTTP/1.1" 500 -
    '''
    id_user = request.args.get("id")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    timeReqvest = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  #Определяем время прихода запроса

    # Вставляем данные в таблицу

    with sqlite3.connect(config['BD']) as conn:
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO GPS_table VALUES (?,?,?,?)", [(timeReqvest, lat, lon, id_user)])
        conn.commit()

    print("*"*10)
    print("get_GPS")
    print(id_user, lat, lon)
    print("*" * 10)
    return lat, lon

@app.route("/Tracking", methods=["GET"])
def getTracking():
    '''
    получает id пользователя и отдает его координаты
    :return:
     #[18 / Aug / 2019 11: 38:05] "GET /test?lat=55.3514818&lon=86.0935871 HTTP/1.1"
     217.118.79.42 - -     "GET /test?id=123&lat=55.3516896&lon=86.0940981 HTTP/1.1" 500 -
    '''
    id_user = request.args.get("id")

    lat, lon, data, danger = get_last_GPS(id_user)
    return redirect('topic/%s/%s/%s/%s' % (lat, lon, data, danger))


def getPointOfBD(id):
    '''
    Получаем последнюю информацию по id пользователя
    :param id:
    :return: ('2019-08-18 16:25:26', 55.351393, 86.0938722, 1256)
    '''
    with sqlite3.connect(config['BD']) as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM GPS_table WHERE id=?"
        cursor.execute(sql, [(id)])
        data = cursor.fetchall()
        return data[-1]

def contactСheck(contact):
    for i in contact:
        if len(i) > 0:
            return True
        else:
            return False

def get_last_GPS(id):
    '''
    Получает id пользователя и возварщает полледнюю записанную координату
    :param id:
    :return:
    '''
    print("get_last_GPS", id)
    print(getPointOfBD(id))
    data, lat, lon, id_user = getPointOfBD(id)
    print("___" * 10)
    print(data, lat, lon, id_user)
    print("___"*10)
    # lat = 55.3514818
    # lon = 86.0935871
    current_GPS = Point(lat, lon, 'epsg:4326')
    current_GPS = Point(lon, lat, 'epsg:4326')
    contact = analitic_user.getPoligonContact(current_GPS, 0.0001)
    if contactСheck(contact):
        danger = 'Близость воды'
        print(danger,'*'*10)
    else:
        danger = 'Опасность отсутствует'

    return lat, lon, data, danger


@app.route('/topic/<lat>/<lon>/<data>/<danger>')
def show_topic(lat, lon, data, danger):

    return '''%s, %s, %s, %s''' % (lat, lon, data, danger)


if __name__ == "__main__":

    app.debug = True
    app.run(host='0.0.0.0', port=256)