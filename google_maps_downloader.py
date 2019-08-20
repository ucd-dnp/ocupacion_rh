# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:52:56 2019

@author: hinsuasti
"""

import urllib
import os
import math
import pyproj
from PIL import Image
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

class GoogleMapDownloader:
    """
        A class which generates high resolution google maps images given
        a longitude, latitude and zoom level
    """

    def __init__(self, coords= None, zoom=17, tile_size=256, proj=None,
                 PIXEL_SIZE_X = 1.1937, PIXEL_SIZE_Y= 1.1860):
        """
            GoogleMapDownloader Constructor

            Args:
                coords:     coordinate Box, (left, top, right, bottom)
                zoom:       The zoom level of the location required, 
                            ranges from 0 - 23.  defaults to 12
                tile_size:  Size for tile of google maps
                proj:       image crs.
                PIXEL_SIZE_X: pixel size on image (meters) x direction
                PIXEL_SIZE_Y: pixel size on image (meters) y direction
        """
        self._coords = coords
        self._xtile = None
        self._ytile = None
        self._zoom = zoom
        self.map_img = None
        self.proj = proj
        self._tile_size = tile_size
        self._tile_width = None
        self._tile_height = None
        self._psx = PIXEL_SIZE_X
        self._psy = PIXEL_SIZE_Y
        self._ntiles = self.computeNtiles()
        self.generateGTmatrix()
    
    
    def computeNtiles(self):
        """
            Computes the number of necessary tiles to generate the satellital
            image given the box coords
            
            Returns: number of tiles
        """
        x_start, y_start = self.getXY()
        x_end, y_end = self.getXY(lat=self._coords[2], lon = self._coords[3])
        xtiles = (x_end - x_start) + 1
        ytiles = (y_end - y_start) + 1
        self._tile_width = xtiles
        self._tile_height= ytiles
        return  xtiles*ytiles
    
    def getLonLat(self):
        """
            Generates an Lat, Lng tile coordinate based on x and y coordinate
            reference system projection and zoom level
            
            Retuns:  An Lat, Lng tile coordinate
        """
        n = 2.0 ** self._zoom
        lon_deg = self._xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * self._ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def getXY(self, **kwargs):
        """
            Generates an X,Y tile coordinate based on the latitude, longitude 
            and zoom level

            Returns:    An X,Y tile coordinate
        """
        lon = kwargs.get('lon', self._coords[1])
        lat = kwargs.get('lat', self._coords[0])
        lat_rad = math.radians(lat)
        n = 2.0 ** self._zoom
        self._xtile = int((lon + 180.0) / 360.0 * n)
        self._ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (self._xtile, self._ytile)
    
    def getXYproj(self, **kwars):
        """
            Generates an X,Y tile coordinate based on the latitude, longitude 
            and zoom level

            Returns:    An X,Y tile coordinate
        """
        lon = kwars.get('lon', self._coords[1])
        lat = kwars.get('lat', self._coords[0])
        
        srcProj = pyproj.Proj(init='epsg:4326', preserve_units=True)
        dstProj = pyproj.Proj(init=self.proj, preserve_units=True)

        point_x, point_y = pyproj.transform(srcProj, dstProj, lon, lat)

        return int(point_x), int(point_y)
    
    def generateGTmatrix(self):
        """
            Generates the Geo Transform matrix to map a pixel coordinate to a 
            georeferenced lat, lnt coordinates.
            
            Returns:  A geoTransform matrix. Shape (2,3)
        """
        x_min, y_max = self.getXYproj()
        self.GT =  np.array([[x_min,self._psx, 0],[y_max, 0, -self._psy]])

    def generateImage(self, **kwargs):
        """
            Generates an image by stitching a number of google map tiles together.
            
            Args:
                start_x:        The top-left x-tile coordinate
                start_y:        The top-left y-tile coordinate
                tile_width:     The number of tiles wide the image should be -
                                defaults to 5
                tile_height:    The number of tiles high the image should be -
                                defaults to 5
            Returns:
                A high-resolution Google Map image.
        """
        tile_size = self._tile_size
        start_x = kwargs.get('start_x', None)
        start_y = kwargs.get('start_y', None)
        tile_width = kwargs.get('tile_width', self._tile_width)
        tile_height = kwargs.get('tile_height', self._tile_height)

        # Check that we have x and y tile coordinates
        if start_x == None or start_y == None :
            start_x, start_y = self.getXY()

        # Determine the size of the image
        width, height = tile_size * tile_width, tile_size * tile_height

        #Create a new image of the size require
        self.map_img = Image.new('RGB', (width,height))

        for x in range(0, tile_width):
            for y in range(0, tile_height) :
                #url = 'https://mt1.google.com/vt/lyrs=s&?x=' + str(start_x + x) + '&y=' + str(start_y + y) + '&z=' + str( self._zoom)
                url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/' + str(self._zoom) + '/' + str(start_y + y) + '/' +str(start_x + x)
                current_tile = str(x)+'-'+str(y)
                urllib.request.urlretrieve(url,current_tile)
            
                im = Image.open(current_tile)
                self.map_img.paste(im, (x*tile_size, y*tile_size))
              
                os.remove(current_tile)

        return self.map_img
    
    
    def save_raster(self, src, filepath):
        
        #https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames  -> section Resoluton and scale
        PIXEL_SIZE_X = 1.1937
        PIXEL_SIZE_Y = 1.186
        x_pixels = self._tile_width*self._tile_size
        y_pixels = self._tile_height*self._tile_size
        
        lat, lon = self.getLonLat()
        x_min, y_max = self.getXYproj(lon=lon, lat=lat)
        wkt_projection = pyproj.Proj(init=self.proj).definition_string()
        
        driver = gdal.GetDriverByName('GTiff')
        
        dataset = driver.Create(filepath, x_pixels, y_pixels, 3, 
                                gdal.GDT_Float32)
        
        dataset.SetGeoTransform((x_min, PIXEL_SIZE_X, 0,
                                 y_max   , 0, -PIXEL_SIZE_Y))
        
        dataset.SetProjection(wkt_projection)
        dataset.GetRasterBand(1).WriteArray(src[:,:,0])
        dataset.GetRasterBand(2).WriteArray(src[:,:,1])
        dataset.GetRasterBand(3).WriteArray(src[:,:,2])
        dataset.FlushCache()
        

def main():
    # Create a new instance of GoogleMap Downloader
    proj = 'epsg:32618'
    name = 'prueba_sp.tif'
    #lat , lon  =1.1673, -76.6629 # mocoax
    box = (-0.180455, -74.795327, -0.201998, -74.770565)
    gmd = GoogleMapDownloader(coords=box, zoom=17, proj=proj, tile_height=11, tile_width= 8)

    print("The tile coorindates are {}".format(gmd.getXY()))
    print(gmd._ntiles)
    #print("lat / lon coordinates are ({}, {})".format(lat, lon))  
    #print("lat / lon coordinates are {}".format(gmd.getLonLat()))  
    try:
        # Get the high resolution image
        img = gmd.generateImage()
        img = np.array(img)
        plt.imshow(img)
        plt.axis('off')
        gmd.save_raster(img,name)
    except IOError:
        print("Could not generate the image - try adjusting the zoom level and checking your coordinates")
    else:
        #Save the image to disk
        #img.save("data/images/high_resolution_image.png")
        print("The map has successfully been created")


if __name__ == '__main__':  main()