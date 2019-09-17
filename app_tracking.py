from moduls.modul_analitic import analitic
from moduls.WMS_geoServer import WMS, Point
from datetime import datetime
import sqlite3
import simplekml
import os

class tracking:
    def __init__(self, pathBD, list_shp_oms, URL_WMS, layers_WMS, path_save_image):
        ##BD
        self.conn = sqlite3.connect(pathBD)
        self.cursor = self.conn.cursor()
        #Analitic
        self.analitic = analitic(list_shp_oms)

        #WMS Server
        self.wms = WMS(URL_WMS, layers_WMS)

        #TEMP
        self.last_working_date = datetime.strptime("2019-08-18 15:32:48", "%Y-%m-%d %H:%M:%S")  #Последняя обработка

        #Settings
        self.path_save_image = path_save_image

    def getPointOfBD(self, id):
        '''
        Получаем последнюю информацию по id пользователя
        :param id:
        :return: ('2019-08-18 16:25:26', 55.351393, 86.0938722, 1256)
        '''
        sql = "SELECT * FROM GPS_table WHERE id=?"
        self.cursor.execute(sql, [(id)])
        data = self.cursor.fetchall()
        return data[-1]

    def __converter_time(self, time: str):
        '''
        Конвертируем время из формата в БД в объект времяни
        :param time:
        :return:
        '''
        #2019-08-18 15:32:48
        dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        return dt

    def __PoligonContact(self, point_GPS:Point, radius=0.001):
        '''
        Возвращает результат пересечений
        :param point_GPS:
        :param radius:
        :return:
        '''
        contact = self.analitic.getPoligonContact(point_GPS, radius=radius)
        return contact

    def __get_image_WMS(self, point: Point, size=15, coefficient=3):
        bbox = point.createBbox(size, coefficient)
        self.wms.getImage(bbox, self.path_save_image)

    def contactСheck(self, contact):
        for i in contact:
            if len(i) > 0:
                return True
            else:
                return False

    def get_All_KML(self, id, path, name):
        kml = simplekml.Kml()
        #Получаем данные по определеннуму ID
        sql = "SELECT * FROM GPS_table WHERE id=?"
        self.cursor.execute(sql, [(id)])
        data = self.cursor.fetchall()

        for point in data:
            kml.newpoint(name="Kirstenbosch", coords=[(point[2], point[1])])

        pathSaveKML = os.path.join(path, name + '.kml')
        kml.save(pathSaveKML)

    def run(self, id, radius=1):
        while True:
            current_values_from = self.getPointOfBD(id)
            if self.last_working_date < self.__converter_time(current_values_from[0]): #Проверка на последнее обновления
                self.last_working_date = self.__converter_time(current_values_from[0])
                pointGPS = Point(current_values_from[1], current_values_from[2], 'epsg:4326')  # создаем точку в пространстве
                contact = self.__PoligonContact(pointGPS, radius=radius)  #Проверяем на совподения с указанными полигонами
                if self.contactСheck(contact):  #Если полигоны найдены то
                    self.__get_image_WMS(pointGPS)
                    print("Есть соприкосновения")



if __name__ == '__main__':
    #База данных
    pathBD = r'/home/dima/ServerPython/androindServerMap/bd'
    #Слои для проверок
    list_shp_oms = [r"./shp/water-polygon/water-polygon.shp"]
    #WMS
    URL_WMS = r'http://82.179.4.198:8080/geoserver/Kemerovo/wms'
    layers_WMS = r'layers=Kemerovo%3Achast_mozhuh'
    path_save_image = './image/'

    test = tracking(pathBD, list_shp_oms, URL_WMS, layers_WMS, path_save_image)
    test.get_All_KML(1256, '', 'test2')
    print("ok")
    test.run(1256, 0.001)