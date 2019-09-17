'''
Модуль для взаимодействия с WMS сервисом
'''

import numpy
import requests
import shutil
from pyproj import Proj, transform
import os

#Пример
#"http://82.179.4.198:8080/geoserver/Kemerovo/wms?service=WMS&version=1.1.0&request=GetMap&layers=Kemerovo%3Achast_mozhuh&bbox=85.9147809027472%2C55.377472103044006%2C85.9927392160472%2C55.400313436479&width=768&height=330&srs=EPSG%3A4326&format=image/png"


STANDART_PARAMETRS = { #Стандартные параметры
            'version': 'version=1.1.0',
            'service': 'service=WMS',
            'request': 'request=GetMap',
            'srs': 'srs=EPSG%3A4326',
            'format': 'format=image/png'}

#'layers': "layers=Kemerovo%3Achast_mozhuh"

class Bbox:
    '''
    Структура для определения зоны вырезки изображения
    '''
    def __init__(self, lat_loint_A, lon_loint_A, lat_loint_B, lon_loint_B, width, height):
        self.lat_loint_A = lat_loint_A
        self.lon_loint_A = lon_loint_A

        self.lat_loint_B = lat_loint_B
        self.lon_loint_B = lon_loint_B

        self.width = width
        self.height = height


class Point:
    def __init__(self, lat=None, lon=None, srs: str=''):
        self.lat = lat
        self.lon = lon
        self.srs = srs

    def createBbox(self, size, coefficient=3) -> Bbox:
        '''
        Создает bbox и возвращает bbox
        :return:
        '''
        #СК используемые
        input_proj = Proj(init=self.srs)
        UTM_45N_Proj = Proj(init='epsg:32645')

        temp_lat, temp_lon = transform(input_proj, UTM_45N_Proj, self.lat, self.lon)

        lat_A, lon_A = transform(UTM_45N_Proj, input_proj, temp_lat + size, temp_lon - size)
        lat_B, lon_B = transform(UTM_45N_Proj, input_proj, temp_lat - size, temp_lon + size)

        bbox = Bbox(lat_A, lon_A, lat_B, lon_B, size*coefficient, size*coefficient)
        return bbox

    def __repr__(self):
        return "lat= " + str(self.lat) + " lon= " + str(self.lon) + ' srs= ' + self.srs

class WMS:

    PARAM_GET = {
        'bbox': 'bbox=',
        'width': 'width=',
        'height': 'height='}

    def __init__(self, URL_WMS, layers, param=STANDART_PARAMETRS):
        self.URL_WMS = URL_WMS
        #self.layers = layers
        self.param = param

        STANDART_PARAMETRS.update({'layers': layers})

    def getImage(self, bbox, path_save) -> numpy.ndarray:
        '''
        Сохранить изображения и возвращает изоюражения
        :param path_save:
        :return: возвращает изображения
        '''
        dict_param_Bbox = self.__fill_parametrs(bbox)
        URL = self.__convertDictToStr(dict_param_Bbox)
        print(URL)
        name = self.__get_name_image(bbox)

        image = self.__getImage(URL, path_save, name)
        return image

    def __fill_parametrs(self, bbox: Bbox):
        '''Формирует данные для заполнения'''
        # bbox=85.9147809027472%2C55.377472103044006%2C85.9927392160472%2C55.400313436479
        dict_param_Bbox = {}
        dict_param_Bbox['bbox'] = self.PARAM_GET['bbox'] + '{0}%2C{1}%2C{2}%2C{3}'.format(bbox.lat_loint_B, bbox.lon_loint_A, bbox.lat_loint_A, bbox.lon_loint_B)
        dict_param_Bbox['width'] = self.PARAM_GET['width'] + str(bbox.width)
        dict_param_Bbox['height'] = self.PARAM_GET['height'] + str(bbox.height)
        return dict_param_Bbox

    def __convertDictToStr(self, dict_param_Bbox: dict):
        '''
        Сводим все вместе и получает готовый запрос
        :param request:
        :return:
        '''
        dict_param_Bbox.update(self.param)
        request = ''
        for name in dict_param_Bbox:
            request = request + '&' + dict_param_Bbox[name]
        request = request[1:]
        request = self.URL_WMS + '?' + request
        return request

    def __get_name_image(self, Bbox):
        '''Получаем имя файла изображения'''
        name = 'image_test'
        return name

    def __getImage(self, url, path_dir, name, format='.png'):
        '''
        Забирает изобрадения с сервера и вохраняет его на диск
        :param url:
        :param path_dir:
        :param name:
        :param format:
        :return:
        '''
        response = requests.get(url, stream=True)
        path = os.path.join(path_dir, name + format)
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


if __name__ == '__main__':
    URL = r'http://82.179.4.198:8080/geoserver/Kemerovo/wms'
    layers = r'layers=Kemerovo%3Achast_mozhuh'

    geoServer = WMS(URL, layers)
    GPS = Point(85.943097, 55.392152, 'epsg:4326')
    bbox = GPS.createBbox(15, 100)
    geoServer.getImage(bbox, './image/')




