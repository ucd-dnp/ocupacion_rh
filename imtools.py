# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 08:56:47 2019

@author: hinsuasti

util functions 
"""
from collections import defaultdict

import numpy as np
import cv2
import tifffile as tiff
from shapely.geometry import MultiPolygon, Polygon
from skimage.exposure import equalize_adapthist, equalize_hist
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool
import time
import geopandas as gpd
from functools import reduce
import operator
import math


class imtools():

    def equalize_histogram(image, adaptative = False):
        temp = image.copy()
        for ich in range(temp.shape[2]):
            im = temp[:,:,ich]
            if not adaptative:
                im = equalize_hist(im)
            else:
                im = equalize_adapthist(im)
                
            temp[:,:,ich] = im
        
        return temp.astype('float32')

    def Feature_im2hist(image, segments, nbins=16, clrSpc= 'hsv',threads = 30):
        start = time.time()
        print('--- Computing image features ---')
        n_seg = np.unique(segments)
        Xfeat = np.zeros((len(n_seg),3*nbins),dtype=np.float32)
        def poolCalcHist(idx):
             mask = np.zeros(image.shape[:2],dtype= np.uint8)
             mask[segments == idx] = 255
             Npixels = len(mask[segments==idx])
             if clrSpc == 'hsv':
                 Xfeat[idx,:nbins] = (cv2.calcHist([image],[0], mask,[nbins],[0,179]).transpose())/Npixels
             else:
                 Xfeat[idx,:nbins] = (cv2.calcHist([image],[0], mask,[nbins],[0,255]).transpose())/Npixels
             Xfeat[idx,nbins:2*nbins] = (cv2.calcHist([image],[1], mask,[nbins],[0,255]).transpose())/Npixels
             Xfeat[idx,2*nbins:3*nbins] = (cv2.calcHist([image],[2], mask,[nbins],[0,255]).transpose())/Npixels
                 
        pool = Pool(threads)
        pool.map(poolCalcHist,n_seg)
        pool.close()
        pool.join()
                
        print('Done!, Execution time: ',time.time() - start)
        return Xfeat

    def draw_GT(im,labels,segments):
        idx = np.unique(segments)[labels==1]
        mask = np.isin(segments,idx).astype('uint8')
        GT = cv2.bitwise_and(im,im,mask=mask)
        plt.figure()
        plt.imshow(GT)
        plt.axis('off')
        return mask
    
    def get_scalers(image, x_max, y_min):
        h, w = image.shape[:2]
        w_ = w * (w / (w + 1))
        h_ = h * (h / (h + 1))
        
        return w_ / x_max, h_ / y_min
    
    def mask_for_polygons(shape, polygons):
        img_mask = np.zeros(shape, np.uint8)
        if not polygons:
            return img_mask
        int_coords = lambda x: np.array(x).round().astype(np.int32)
        exteriors = [int_coords(poly.exterior.coords) for poly in polygons]
        interiors = [int_coords(pi.coords) for poly in polygons
                     for pi in poly.interiors]
        cv2.fillPoly(img_mask, exteriors, 1)
        cv2.fillPoly(img_mask, interiors, 0)
        return img_mask
        
    def mask_to_polygons(mask, epsilon=20.0, min_area=7.0):
        # first, find contours with cv2: it's much faster than shapely
        contours, hierarchy = cv2.findContours(
            ((mask == 1) * 255).astype(np.uint8),
            cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)
        # create approximate contours to have reasonable size
        approx_contours = [cv2.approxPolyDP(cnt, epsilon, True)
                           for cnt in contours]
        if not contours:
            return MultiPolygon()
        # now messy stuff to associate parent and child contours
        cnt_children = defaultdict(list)
        child_contours = set()
        assert hierarchy.shape[0] == 1
        # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
        for idx, (_, _, _, parent_idx) in enumerate(hierarchy[0]):
            if parent_idx != -1:
                child_contours.add(idx)
                cnt_children[parent_idx].append(approx_contours[idx])
        # create actual polygons filtering by area (removes artifacts)
        all_polygons = []
        for idx, cnt in enumerate(approx_contours):
            if idx not in child_contours and cv2.contourArea(cnt) >= min_area:
                assert cnt.shape[1] == 1
                poly = Polygon(
                    shell=cnt[:, 0, :],
                    holes=[c[:, 0, :] for c in cnt_children.get(idx, [])
                           if cv2.contourArea(c) >= min_area])
                all_polygons.append(poly)
        # approximating polygons might have created invalid ones, fix them
        all_polygons = MultiPolygon(all_polygons)
        if not all_polygons.is_valid:
            all_polygons = all_polygons.buffer(0)
            # Sometimes buffer() converts a simple Multipolygon to just a Polygon,
            # need to keep it a Multi throughout
            if all_polygons.type == 'Polygon':
                all_polygons = MultiPolygon([all_polygons])
        return all_polygons
        
    def rescale_intensity(image):
        temp = image.copy()
        temp = (temp - temp.min())/(temp.max() - temp.min())
        return temp.astype('float32')

    def scale_percentile(image):
        vmin = np.percentile(image, 2.0)
        vmax = np.percentile(image, 98.0)
        temp = image.copy()
        temp[temp<vmin] = vmin
        temp[temp>vmax] = vmax
        temp = imtools.rescale_intensity(temp)
        return temp.astype('float32')

    def scale_percentile_by_channel(image):
        temp = image.copy()
        for ich in range(temp.shape[2]):
            im = temp[:,:,ich]
            vmin = np.percentile(im, 2.0)
            vmax = np.percentile(im, 98.0)
            im[im<vmin] = vmin
            im[im>vmax] = vmax
            im = (im - im.min()) / (im.max() - im.min())
            temp[:,:,ich] = im
            
        return temp.astype('float32')
        
    def show_mask(m):
        # hack for nice display
        tiff.imshow(255 * np.stack([m, m, m]));
    
    
    def smooth_image(image, alpha = 5):
        temp = np.asarray(255*image,dtype = np.uint8)
        temp = cv2.GaussianBlur(temp,(alpha,alpha),0)
        temp = imtools.rescale_intensity(temp)
        return temp.astype('float32')

    
    def sp2latlon(coords, GT):
        temp = np.dot(GT[:,1:],coords.transpose()[::-1,:]) + np.reshape(GT[:,0],(2,1))
        temp = temp.transpose()
        center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), temp), [len(temp)] * 2))
        pnt_xy = sorted(temp, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)
        pnt_xy = list(map(lambda x: tuple(x),pnt_xy))
        return Polygon(pnt_xy)
    
    def mapSuperPixels(coords = None, GT =None, proj ={'init':'epsg:32618'} , verbose= False,):
        start = time.time()
        if verbose: print('---  Mapping superpixels to lat/lng coordinates  ---')
        Polygons = list()
        for c in coords:
            if len(c)>2:
                Polygons.append(imtools.sp2latlon(c,GT))
        if len(Polygons)==1:
            geometries = gpd.GeoDataFrame({'geometry':Polygons},
                                          geometry='geometry',
                                          crs = proj,
                                          index = [0])
        else:
            geometries = gpd.GeoDataFrame({'geometry':Polygons},
                                          geometry='geometry',
                                          crs = proj)
            
        if verbose: print('Done!, exceution time:  ', time.time()-start)
        geometries.to_crs({'init':'epsg:4326'})
        return geometries
    
        
            
    
        