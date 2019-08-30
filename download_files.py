
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

#libraries needed for deleting files
import shutil

# code taken from: https://www.tutorialspoint.com/How-to-create-a-zip-file-using-Python
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

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
            rivers_path = "{}/{}".format(self.path, name)
            #create the directory for then zipping on a .zip
            os.mkdir(rivers_path)

            #fixing the rivers geopandas
           
            rivers.to_file("{}/{}.shp".format(rivers_path, name))
            #creating the zipfile
            zip_rivers = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #zipping all files on specified folder
            zipdir(rivers_path, zip_rivers)
            #closing the zip
            zip_rivers.close()
            shutil.rmtree(rivers_path)
            rivers.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            

            list_file.append((label, name))
        if builds is not None:
            label = "Capa de construcciones"
            name = "builds_layer"
            builds_path = "{}/{}".format(self.path, name)
            #create the directory for then zipping on a .zip
            os.mkdir(builds_path)

            builds.to_file("{}/{}.shp".format(builds_path, name))
            zip_builds = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #zipping all files on specified folder
            zipdir(builds_path, zip_builds)
            #closing the zip 
            zip_builds.close()
            shutil.rmtree(builds_path)
            builds.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            

       
            list_file.append((label, name))
        if roi is not None:
            label = "Capa de regiones"
            name = "roi_layer"

            rois_path = "{}/{}".format(self.path, name)
            #create the directory for then zipping on a .zip
            os.mkdir(rois_path)

            roi.to_file("{}/{}.shp".format(rois_path, name))
            zip_rois = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #zipping all files on specified folder
            zipdir(rois_path, zip_rois)
            #closing the zip
            zip_rois.close()
            shutil.rmtree(rois_path)
            roi.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')


            list_file.append((label, name))
        
        content = []
        if not list_file:
            content.append(html.Label("Aún no se encuentran capas para descargar",
                                style = {
                                    "font-size" : '14px'
                                }))
        else:
            #creating download links with existing layers
            for i in range(len(list_file)):
                file_1 = self.file_download_link("{}{}".format(list_file[i][1], ".zip"))
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




