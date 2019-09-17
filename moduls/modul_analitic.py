import os
import geopandas as gp
from moduls.WMS_geoServer import Point
from shapely.geometry import LineString

class analitic:
    poligon_shp_osm = []
    def __init__(self, list_file_shp):
        for shp in list_file_shp:
            self.poligon_shp_osm.append(gp.read_file(shp))

    def getPoligonContact(self, point: Point, radius=0.001):
        '''
        Проверяет двнную точку со всеми слоями опасностей и возвращает список cовподений
        :param point:
        :param radius: разиус в котором необходимо искать
        :return:
        '''
        point = gp.geoseries.Point((point.lat, point.lon))
        pointBuffer = point.buffer(radius)
        poligin_contact = []
        for poligon_OMS in self.poligon_shp_osm:
            temp = self.__getContact(pointBuffer, poligon_OMS)
            poligin_contact.append(temp)
        #print(poligin_contact)
        #print("Количество найденных полигонов: ", len(poligin_contact))
        return poligin_contact

    def __getContact(self, pointBuffer, poligon_OMS):
        '''
        Принимает полигон круга и полигону слоя и возвращает полигоны сопрекосновения
        :param pointBuffer:
        :param poligon_OMS:
        :return:
        '''
        data = []
        for index, orig in poligon_OMS.iterrows():
            if pointBuffer.intersects(orig['geometry']):
                OSM_ID = orig['OSM_ID']
                data.append({'geometry': pointBuffer.intersection(orig['geometry']), 'OSM_ID': OSM_ID})
        return data

    def save_shp(self, poligin_contact, path=r'shp\test', name=r'linestring_intersection.shp'):
        for i in poligin_contact[0]:
            geom = i['geometry']
            if geom.geom_type == 'Polygon':
                i['geometry'] = LineString(list(geom.exterior.coords))

        df = gp.GeoDataFrame(poligin_contact, columns=['geometry', 'OSM_ID'])

        df.to_file(os.path.join(path, name))

if __name__ == '__main__':
    # list_shp_oms = [r"D:\cmitd\Documents\test\shp\water-polygon\water-polygon.shp"]
    # list_shp_oms = [r"./shp/water-polygon/water-polygon.shp"]
    list_shp_oms = [r"/home/dima/ServerPython/androindServerMap/shp/water-polygon/water-polygon.shp"]
    test = analitic(list_shp_oms)


    lat = 86.088691
    lon = 55.359739
    # lat = 86.05405
    # lon = 55.35404

    point_GPS = Point(lat, lon, 'epsg:4326')
    contact = test.getPoligonContact(point_GPS, 0.001)

    #test.save_shp(contact)  ## Неработает

    print(len(contact))
    print(contact)