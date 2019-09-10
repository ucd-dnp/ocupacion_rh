# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:17:16 2019

@author: hinsuasti

Libreria que controla todo lo de Folium
genera mapa base 
"""

import folium
from folium.plugins import FloatImage
IMAGE = ("https://raw.githubusercontent.com/davidinsuasty/git_tutorial/master/icons/compass_icon.png")
class Map:
    '''
        A class to generate tile map
    '''
    # google: "http://mt1.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
    # argis: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    #https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'
    def __init__(self, zoom = 13, location = None,
                 satellital_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'):
        self._zoom = zoom
        self._location = location
        self._url = satellital_url
    


    def generatePDFMap(self, builds, rivers, roi, 
                    poly_rivers, superpixels, bounding):
        
        _map = folium.Map(width = 700, height = 500, location= self._location, zoom_start=self._zoom,
                          attr='Análisis susceptibilidad de inundación',
                          max_zoom=18, min_zoom= 10)
       
        FloatImage(IMAGE,bottom= 81 ,left=2).add_to(_map)
        _map.add_tile_layer(self._url, name='Satelital',
                            attr='Análisis susceptibilidad de inundación',
                            max_zoom=17, min_zoom=10)
        _map.add_child(folium.LatLngPopup())
       
        
        if builds is not None:
            gjson = builds.to_json()
            lay_builds = folium.FeatureGroup(name='Construcciones susceptibles')
            lay_builds.add_child(folium.GeoJson(data=gjson,
                                                style_function= lambda x:
                                                    {'color':'#000000',
                                                     'weight':0.15,
                                                     'fillColor':'#F08615',
                                                     'fillOpacity': 1.0}))
            _map.add_child(lay_builds)
           
        if superpixels is not None:
            gjson = superpixels.to_json()
            lay_sp = folium.FeatureGroup(name='Zonas susceptibles')
            lay_sp.add_child(folium.GeoJson(data=gjson,
                                            style_function= lambda x:
                                                {'color':'#3DCF58',
                                                 'weight':0.15,
                                                 'fillColor':'#3DCF58',
                                                 'fillOpacity':0.4}))
            _map.add_child(lay_sp)
            
        
        if rivers is not None:
            gjson = rivers.to_json()
            lay_rivers = folium.FeatureGroup(name='Rios')
            lay_rivers.add_child(folium.GeoJson(data= gjson,
                                                style_function=lambda x: 
                                                    {'color':'#0083E9', 
                                                     'opacity':0.8,
                                                     'fillColor':'#0083E9', 
                                                     'fillOpacity': 1,
                                                     'width':0.1}))
            if poly_rivers is not None:
                gjson = poly_rivers.to_json()
                lay_rivers.add_child(folium.GeoJson(data = gjson,
                                                    style_function=lambda x: 
                                                    {'color':'#0083E9', 
                                                     'opacity':0.8,
                                                     'fillColor':'#0083E9', 
                                                     'fillOpacity': 1,
                                                     'width':0.1}))
            _map.add_child(lay_rivers)
           
            
        if roi is not None:
            gjson = roi.to_json()
            lay_susceptibilidad = folium.FeatureGroup(name="Zona de susceptibilidad")
            lay_susceptibilidad.add_child(folium.GeoJson(data= gjson,
                                                         style_function=lambda x: 
                                                             {'color':'#B70015',
                                                              'opacity':0.2,
                                                              'fillColor':'#B70015', 
                                                              'fillOpacity': 0.3,
                                                              'width':0.1}))
            _map.add_child(lay_susceptibilidad)
             #_map2 es creado para ponerlo en el reporte pdf
            # _map2.add_child(lay_susceptibilidad)
        
        if bounding is not None:
            lat2,lon1,lat1,lon2 = bounding
            points = [(lat1,lon1),(lat1,lon2),(lat2,lon2),(lat2,lon1),(lat1,lon1)]
            folium.PolyLine(points,weight=1.5,opacity = 0.5, dashArray=[20,20],dashOffset= 20).add_to(_map)
            
        _map.add_child(folium.LayerControl())
         #_map2 es creado para ponerlo en el reporte pdf
        # _map2.add_child(folium.LayerControl())
        
        
        _map.save('temp2.html')
       
        

    def generateMap(self, builds = None, rivers = None, roi = None, 
                    poly_rivers = None, superpixels = None, bounding = None):
        
        self.generatePDFMap(builds, rivers, roi, poly_rivers, superpixels, bounding)

        _map = folium.Map(location = self._location, zoom_start=self._zoom,
                          attr='Análisis susceptibilidad de inundación',
                          max_zoom=18, min_zoom= 10)

        
        #_map2 es creado para ponerlo en el reporte pdf
        # _map2 = folium.Map(width = 540,height = 540, location = self._location, zoom_start=self._zoom,
        #                   attr='Análisis susceptibilidad de inundación',
        #                   max_zoom=18, min_zoom= 10)
        FloatImage(IMAGE,bottom= 81 ,left=2).add_to(_map)
        _map.add_tile_layer(self._url, name='Satelital',
                            attr='Análisis susceptibilidad de inundación',
                            max_zoom=17, min_zoom=10)
        _map.add_child(folium.LatLngPopup())
         #_map2 es creado para ponerlo en el reporte pdf
        # _map2.add_tile_layer(self._url, name='Satelital',
        #                     attr='Análisis susceptibilidad de inundación',
        #                     max_zoom=17, min_zoom=10)
        # _map2.add_child(folium.LatLngPopup())
        
        if builds is not None:
            gjson = builds.to_json()
            lay_builds = folium.FeatureGroup(name='Construcciones susceptibles')
            lay_builds.add_child(folium.GeoJson(data=gjson,
                                                style_function= lambda x:
                                                    {'color':'#000000',
                                                     'weight':0.15,
                                                     'fillColor':'#F08615',
                                                     'fillOpacity': 1.0}))
            _map.add_child(lay_builds)
             #_map2 es creado para ponerlo en el reporte pdf
            # _map2.add_child(lay_builds)
            
        if superpixels is not None:
            gjson = superpixels.to_json()
            lay_sp = folium.FeatureGroup(name='Zonas susceptibles')
            lay_sp.add_child(folium.GeoJson(data=gjson,
                                            style_function= lambda x:
                                                {'color':'#3DCF58',
                                                 'weight':0.15,
                                                 'fillColor':'#3DCF58',
                                                 'fillOpacity':0.4}))
            _map.add_child(lay_sp)
             #_map2 es creado para ponerlo en el reporte pdf
            # _map2.add_child(lay_sp)
        
        if rivers is not None:
            gjson = rivers.to_json()
            lay_rivers = folium.FeatureGroup(name='Rios')
            lay_rivers.add_child(folium.GeoJson(data= gjson,
                                                style_function=lambda x: 
                                                    {'color':'#0083E9', 
                                                     'opacity':0.8,
                                                     'fillColor':'#0083E9', 
                                                     'fillOpacity': 1,
                                                     'width':0.1}))
            if poly_rivers is not None:
                gjson = poly_rivers.to_json()
                lay_rivers.add_child(folium.GeoJson(data = gjson,
                                                    style_function=lambda x: 
                                                    {'color':'#0083E9', 
                                                     'opacity':0.8,
                                                     'fillColor':'#0083E9', 
                                                     'fillOpacity': 1,
                                                     'width':0.1}))
            _map.add_child(lay_rivers)
             #_map2 es creado para ponerlo en el reporte pdf
            # _map2.add_child(lay_rivers)
            
        if roi is not None:
            gjson = roi.to_json()
            lay_susceptibilidad = folium.FeatureGroup(name="Zona de susceptibilidad")
            lay_susceptibilidad.add_child(folium.GeoJson(data= gjson,
                                                         style_function=lambda x: 
                                                             {'color':'#B70015',
                                                              'opacity':0.2,
                                                              'fillColor':'#B70015', 
                                                              'fillOpacity': 0.3,
                                                              'width':0.1}))
            _map.add_child(lay_susceptibilidad)
             #_map2 es creado para ponerlo en el reporte pdf
            # _map2.add_child(lay_susceptibilidad)
        
        if bounding is not None:
            lat2,lon1,lat1,lon2 = bounding
            points = [(lat1,lon1),(lat1,lon2),(lat2,lon2),(lat2,lon1),(lat1,lon1)]
            folium.PolyLine(points,weight=1.5,opacity = 0.5, dashArray=[20,20],dashOffset= 20).add_to(_map)
            
        _map.add_child(folium.LayerControl())
         #_map2 es creado para ponerlo en el reporte pdf
        # _map2.add_child(folium.LayerControl())
        
        
        _map.save('temp.html')
        # _map2 = _map
        # _map2.width = 100
        # _map2.height = 100
        # _map2.save('temp2.html')
        # _map2.save('temp2.html')
        return _map


        
    
    