
#needed libraries for create component
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import geopandas as gpd
#libraries for creating a zipfile
import os
import zipfile




class Download:

    def __init__(self, path):
        self.path = path
    

    def file_download_link(self, filename):
   
        location = "/download/{}".format(filename)
        return html.A(filename, href=location)

    def download_file (self, rivers = None, builds = None, roi = None ):
        list_file = []
        if rivers is not None:
            label = "Capa de rios"
            name = "rivers_layer"
            rivers_f = rivers.drop(labels = "nodes", axis= 1)
            rivers_f.to_file("{}/{}.shp".format(self.path, name))
            rivers_f.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            
            list_file.append((label, name))
        if builds is not None:
            label = "Capa de construcciones"
            name = "builds_layer"
            builds.to_file("{}/{}.shp".format(self.path, name))
            builds.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            
            list_file.append((label, name))
        if roi is not None:
            label = "Capa de regiones"
            name = "roi_layer"
            roi.to_file("{}/{}.shp".format(self.path, name))
            roi.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')

            list_file.append((label, name))
        
        content = []
        if not list_file:
            content.append(html.Label("No se encuentran capas para descargar",
                                style = {
                                    "font-size" : '14px'
                                }))
        else:
            #creating download links with existing layers
            for i in range(len(list_file)):
                file_1 = self.file_download_link("{}{}".format(list_file[i][1], ".shp"))
                file_2 = self.file_download_link("{}{}".format(list_file[i][1], ".geojson"))
                content.append(dbc.Col([
                    dbc.Row(  
                    html.H3(list_file[i][0])
                    ),
                    dbc.Row(
                    file_1
                    ),
                    dbc.Row(
                    file_2
                    )
                ]))

        #create the component to be returned    
        download_component = dbc.Container([
            html.H3("Seleccione cual de los siguientes archivos quiere descargar"),
            dbc.Row(
                content
            )


        ])
        return download_component




