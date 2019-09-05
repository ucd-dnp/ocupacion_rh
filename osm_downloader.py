# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:35:45 2019

@author: hinsuasti
Libreria para decargar información de OSM
"""

#%%  Load necessary libraries
import requests
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import cascaded_union
import geopandas as gpd
import pandas as pd

class OSMDownloader:
    """
        A clas which download the rivers shapes from de interest region
    """

    def __init__(self, box=None,
                 url = "http://overpass-api.de/api/interpreter"):

        self.box = box
        self.url = url
        self._builds = None
        self._rivers = None
        self._poly_rivers = None
    
    def getRiversLayer(self, Type='way', key='waterway'):
        query = f"""
        [out:json];
        ({Type}[{key}]{self.box};);
        out geom;"""
        response = requests.get(self.url,params={'data':query})
        if (response.ok):
            rivers = response.json()
            rivers = gpd.GeoDataFrame(rivers['elements'])
            if len(rivers) == 0:
                self._rivers = -1
                return
            
            rivers.geometry = [LineString([Point(dcc['lon'],dcc['lat']) for dcc in geo]) for geo in rivers.geometry]
            records = pd.DataFrame.from_records(rivers['tags'])
            if 'waterway' in records.columns:
                rivers = rivers.join(records['waterway'])
            if 'intermittent' in records.columns:
                rivers = rivers.join(records['intermittent'])
            if 'tunnel' in records.columns:
                rivers = rivers.join(records['tunnel'])
            
#            if 'intermittent' in rivers.columns:
#                rivers = rivers[rivers['intermittent'] != 'yes']
#            if 'tunnel' in rivers.columns:
#                rivers = rivers[rivers['tunnel'] != 'culvert']
#                rivers = rivers[rivers['tunnel'] != 'yes']
                
            if len(rivers) == 0:
                self._rivers = -1
                return 
            rivers.drop(labels='nodes',axis=1,inplace=True)
            #original coords reference system
            rivers.crs = {'init' :'epsg:4326'}
            #Colombia coords reference system
            #rivers = rivers.to_crs({'init':'epsg:32618'})
            self._rivers = rivers
        else:
            self._rivers = -1
    
    def getRiversPolygons(self,Type='relation', key='waterway'):
        query = f"""
        [out:json];
        ({Type}[{key}]{self.box};);
        out geom;"""
        response = requests.get(self.url,params={'data':query})
        if (response.ok):
            poly_rivers = response.json()
            poly_rivers = poly_rivers['elements']
            if len(poly_rivers) == 0:
                self._poly_rivers = -1
                return 
            Polygons = []
            
            for dc in poly_rivers:
                geotype = dc['tags']['type']
                for members in dc['members']:
                    pt = [(pt['lon'], pt['lat']) for pt in members['geometry']]
                    role = members['role']
                    if geotype == 'multipolygon':    
                        if len(pt)>2 and role =='inner':
                            Polygons.append(Polygon(pt))
                        else:
                            Polygons.append(LineString(pt))
                    else:
                        Polygons.append(LineString(pt))           
            poly_rivers = gpd.GeoDataFrame({'geometry':Polygons},geometry = 'geometry')
            #poly_rivers.geometry = poly_rivers.buffer(0)
            poly_rivers.crs = {'init' :'epsg:4326'}
            #poly_rivers = poly_rivers.to_crs({'init':'epsg:32618'}  )
            
            self._poly_rivers = poly_rivers
        else:
            self._poly_rivers = -1
        
    def getBuildings(self, Type='way', key ='building'):
        query = f"""
        [out:json];
        ({Type}[{key}]{self.box};);
        out geom;"""
        response = requests.get(self.url,params={'data':query})
        if (response.ok):
            buildings = response.json()
            buildings = buildings['elements']
            if len(buildings) < 0:
                self._builds = -1
                return
            self._builds = gpd.GeoDataFrame(geometry=[Polygon([(pt['lon'],pt['lat']) 
                                    for pt in dc['geometry']]) for dc in buildings])
    
            self._builds.set_geometry('geometry', inplace=True, crs = {'init':'epsg:4326'})
            #buildings = buildings_geom.to_crs({'init':'epsg:32618'})
            
        else:
            self._builds = -1  
            
    
    def computeROIsuperpixels(self,buffer=None):
        if type(self._rivers) is not int:
            rivers = self._rivers.to_crs({'init':'epsg:32618'})
            rivers.geometry = [r.buffer(6) if w=='river' else r.buffer(2) 
                                for r, w in zip(rivers.geometry,rivers['waterway'])]
            if type(self._poly_rivers) is not int:
                poly_rivers = self._poly_rivers.to_crs({'init':'epsg:32618'})
                poly_rivers.geometry = poly_rivers.buffer(10)
                
                try:
                    all_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                   geometry='geometry', crs= rivers.crs)
                except:
                    all_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                   geometry='geometry', crs= rivers.crs,
                                                   index = [0])
                    all_rivers.geometry = all_rivers.buffer(20).buffer(-20)
            else:
                try: 
                    all_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                                   geometry='geometry', crs= rivers.crs)
                except:
                    all_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                                   geometry='geometry', crs= rivers.crs,
                                                   index = [0])
                    
            expand_region = all_rivers.buffer(buffer + 20)
            #analysis_region = expand_region.difference(all_rivers)
            return expand_region    

                
if __name__ == '__main__':
    coords = (1.0788, -76.635, 1.0912, -76.6233)
    #buffer de los rios 
    buffer = 35
    #creando objeto osm para descargar información
    osm  = OSMDownloader(box=coords)
   
    #descargando información de rios (solo lineas)
    osm.getRiversLayer()

    osm.getRiversPolygons()
    
    analysis_reg = osm.computeROIsuperpixels(30)
#    poly_rivers.geometry = poly_rivers.geometry.buffer(buffer)
#    
#    #descargando información de construcciones
#    builds = osm.getBuildings()
#    
#    #uniendo los poligonos en una sola region
#    poly_rivers = gpd.GeoDataFrame(cascaded_union(osm._poly_rivers.geometry))
#    poly_rivers.columns = ['geometry']
#    poly_rivers.set_geometry('geometry',inplace= True, crs = rivers.crs)
#    
#    #uniendo los rios en una sola region
#    rivers = gpd.GeoDataFrame(cascaded_union(rivers.geometry))
#    rivers.columns = ['geometry']
#    rivers.set_geometry('geometry', inplace = True, crs = poly_rivers.crs)
#    
#    #uniendo poligonos con rios para crear zona susceptible
#    roi = gpd.GeoDataFrame(cascaded_union(rivers.union(poly_rivers)))
#    roi.columns = ['geometry']
#    roi.set_geometry('geometry', inplace = True, crs = poly_rivers.crs)
#    
#    #graficando
#    ax = builds.plot(color='k')
#    roi.plot(ax = ax, alpha = 0.5)