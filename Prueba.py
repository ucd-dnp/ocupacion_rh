# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:34:27 2019

@author: hinsuasti
"""

from google_maps_downloader import GoogleMapDownloader as GMD
from imtools import imtools
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from shapely.ops import cascaded_union


if __name__ == '__main__':
    
    #### input parameters ###################### 
    proj = 'epsg:32618'
    box = (1.1619,  -76.6503, 1.1528, -76.6450)
    ############################################
    
    ### lo que debo hacer con las capas de los rios de OSM   ###
    rivers.geometry = [r.buffer(6) if w=='river' else r.buffer(2) 
                    for r, w in zip(rivers.geometry,rivers['waterway'])]
    poly_rivers.geometry = poly_rivers.buffer(10)
    
    #union de todos los rios y poligonos
    all_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                      geometry='geometry', crs= rivers.crs)
    all_rivers.geometry = all_rivers.buffer(20).buffer(-20)
    
    expand_rivers_region = all_rivers.buffer(80)
    
    analysis_region = expand_rivers_region.difference(all_rivers)
    #############################################################
    
    ####   generate satellital image  ###########################
    gmd = GMD(coords=box,proj=proj)
    img = np.array(gmd.generateImage(), dtype = np.uint8)
    
    ### mask image and superpixels  ###################
    out, m = imtools.maskRasterIm(img, gmd.GT, analysis_region)
    segments = imtools.computeSegments(out,mask=m)   
    
    #####################################################################
    ##### aqui se deben seleccionar los poligonos que se clasifican como 
    ##### edificación para luego mapear los que sean necesarios
    
    ###  ojo ojo ojo ojo ojo 
    #####################################################################
    seg_polygons = imtools.mapSuperPixels(segments=segments, GT=gmd.GT, verbose=True)
    