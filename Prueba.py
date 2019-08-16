# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:34:27 2019

@author: hinsuasti
"""

from google_maps_downloader import GoogleMapDownloader as GMD
from imtools import imtools
import numpy as np
from skimage.segmentation import quickshift
from skimage.segmentation import mark_boundaries
from skimage.measure import label
from skimage.measure import regionprops, approximate_polygon
from shapely.geometry import Polygon

import matplotlib.pyplot as plt

def mapSuperPixel(coords, GT):
    return np.dot(GT[:,1:],coords.transpose()[::-1,:]) + np.reshape(GT[::-1,0],(2,1))
    

if __name__ == '__main__':
    
    # input parameters 
    proj = 'epsg:32618'
    box = (1.1619,  -76.6503, 1.1528, -76.6450)
    PIXEL_SIZE_X = 1.1937
    PIXEL_SIZE_Y = 1.186
    #object google maps
    gmd = GMD(coords=box,proj=proj)
   
    # Number of tiles for image generation
    print(gmd._ntiles)
   
    #generate satellital image
    img = np.array(gmd.generateImage(), dtype = np.uint8)
    
    segments = quickshift(img,kernel_size=5, convert2lab=True,ratio=1.0,sigma=0.5)
    segments = label(segments,connectivity=2, background=-1)
    for s in np.unique(segments):
        if np.sum(segments==s)< 12:
            segments[segments== s] = -1
   
    props = regionprops(segments)
    
    coords = [approximate_polygon(p.coords,tolerance=0.2) for p in props]
    
    x_min, y_max = gmd.getXYproj()
    GT = np.array([[x_min,PIXEL_SIZE_X, 0],[y_max, 0, -PIXEL_SIZE_Y]])
    