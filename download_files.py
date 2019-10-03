

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import geopandas as gpd

import os
import zipfile

#libreria necesaria para borrar archivos
import shutil


from datetime import datetime

class Download:

    def __init__(self, path):
        self.path = path
        self.date = datetime.now().strftime("%b%d%Y%H%M%S")
        
    """
           Callback para generar y descargar el reporte PDF
            
            Inputs:
                filename:       Escucha si el botón buscar es oprimido
           
            Returns:
                A high-resolution Google Map image.
    """    
    #a partir del nombre del archivo se retorna un botón de dash con hipervinculo al archivo
    def file_download_link(self, filename):
   
        if ".zip" in filename:
            name = "Shapefile"
        else: 
            name = "GeoJSON"
        location = "/download/{}".format(filename)
        link = html.A(name, href=location, style = {
            "text-decoration" : "none",
            "color": "white"
        })
        button = dbc.Button(children = [
            link
        ], size = "sm",
        style = {
            "background" : "#6497b1"
        })
        return button
    """
           Método para comprimir los archivos en el directorio con nombre dado
            
            Inputs:
                path:     Camino hacia el directorio que se desea comprimir
                ziph:     Instancia de Zipfile

    """
    # codigo tomado de: https://www.tutorialspoint.com/How-to-create-a-zip-file-using-Python
    def zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), file)

    """
           Método para generar los botones y vínculos de descarga de archivos
            
            Inputs:
                rivers:     Capa de rios
                builds:     Capa de Construcciones
                roi:        Capa de regiones de suceptibilidad
            
            Returns:
                En caso de que no se le mande ninguna capa, retorna un texto. En caso contrario, retorna
                botones con vinculos a los archivos de las capas.
    """
    def download_file (self, rivers = None, builds = None, roi = None ):
        list_file = []
        if rivers is not None:
            label = "Capa de rios"
            name = "{}rivers_layer".format(self.date)
            rivers_path = "{}/{}".format(self.path, name)
            os.mkdir(rivers_path)
           
            rivers.to_file("{}/{}.shp".format(rivers_path, name))
            
            zip_rivers = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #Se comprimen todos los archivos en el directorio dado
            self.zipdir(rivers_path, zip_rivers, name)
            zip_rivers.close()

            shutil.rmtree(rivers_path)
            rivers.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            

            list_file.append((label, name))

        if builds is not None:
            label = "Capa de construcciones"
            name = "{}builds_layer".format(self.date)
            builds_path = "{}/{}".format(self.path, name)
            os.mkdir(builds_path)

            builds.to_file("{}/{}.shp".format(builds_path, name))
            zip_builds = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #Se comprimen todos los archivos en el directorio dado
            self.zipdir(builds_path, zip_builds, name)
            zip_builds.close()
            shutil.rmtree(builds_path)
            builds.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            
            list_file.append((label, name))
        if roi is not None:
            label = "Capa de regiones"
            name = "{}roi_layer".format(self.date)

            rois_path = "{}/{}".format(self.path, name)
           
            os.mkdir(rois_path)

            roi.to_file("{}/{}.shp".format(rois_path, name))
            zip_rois = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

           #Se comprimen todos los archivos en el directorio dado
            self.zipdir(rois_path, zip_rois, name)
           
            zip_rois.close()
            shutil.rmtree(rois_path)
            roi.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')


            list_file.append((label, name))
        
        #se crean los elementos gráficos que se van a descargar
        content = []
        if not list_file:
            content.append(
                dbc.Col([
                dbc.Row([html.Label("Aún no se encuentran capas para descargar",
                                style = {
                                    "font-size" : '14px'
                                })
                                
                ],justify = "center"),

                dbc.Row([
                    dbc.Spinner(color="primary", type="grow", size = "lg"),
                ],justify = "center")


                ])
            )
            
        else:
            #se crean los botones de descarga con las capas existentes
            for i in range(len(list_file)):
                file_1 = self.file_download_link("{}{}".format(list_file[i][1], ".zip"))
                file_2 = self.file_download_link("{}{}".format(list_file[i][1], ".geojson"))
                content.append(dbc.Col([
                    dbc.Row(  
                    html.B(list_file[i][0])
                    ),
                    dbc.Row([
                    file_1
                    ],
                    style = {
                        "margin-top" : "10px"
                    }),
                    dbc.Row([
                    file_2
                    ],
                    style = {
                        "margin-top" : "10px"
                    })
                ]))

   
        download_component = dbc.Container([
            html.H5("Seleccione cual de los siguientes archivos quiere descargar"),
            dbc.Row(
                content
            )


        ])
        return download_component




