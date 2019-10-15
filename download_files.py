

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

#libreria usada para listar archivos que cumplan una condicion dada
import glob

from datetime import datetime

class Download:

    def __init__(self, path):
        self.path = path
        self.date = datetime.now().strftime("%b%d%Y%H%M%S")
        self.readme = """
        *****************************************************************************************
        Ocupación e infraestructura en zonas de ronda hídrica
        *****************************************************************************************
        Esta herramienta permite aproximar la cantidad de construcciones que están dentro de la 
        ronda de los ríos, a partir de información de capas de ríos y construcciones obtenidas de 
        OpenStreetMap cuando están disponibles. En caso contrario la herramienta utiliza 
        algoritmos de clasificación de imagen para estimar las regiones con construcciones que 
        estén dentro de la ronda de los ríos. 

        Para más información consulte el manual de usuario en: https://planeacionnacional-my.sharepoint.com/:b:/g/personal/ucd_dnp_gov_co/EabRJUEc05hLnlnyORvyYx0BILFyqUGlsh1oxGWKC87qJA?e=hc3JeM
        *****************************************************************************************
        Este reporte contiene información indicativa de las áreas ocupadas y del inventario de la 
        infraestructura ubicada en zonas de rondas hídricas. La información depende de la 
        actualización de los datos de Open Street Map, herramienta de construcción colectiva y no 
        está basada en la cartografía oficial.  La infraestructura en esta área puede estar 
        expuesta a inundaciones, movimientos en masa, procesos erosivos, crecientes súbitas y 
        flujos torrenciales. 

        Los resultados que arroja esta herramienta no sustituyen los estudios y análisis de riesgo 
        para instrumentos de ordenamiento. El DNP no se hace responsable del uso indebido de la 
        información, la cual debe verse como de  referencia.

        ******************************************************************************************
        Herramienta elaborada por el Departamento Nacional de Planeación, en la Dirección de 
        Desarrollo Digital con el apoyo de la Dirección de Ambiente y Desarrollo Sostenible.
        ______________________________
        --------------Licencia pendiente-------------------
        _______________________________

        Bogotá, Colombia, 2019.
        """
        
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
                rivers:       Capa de rios
                builds:       Capa de Construcciones
                roi:          Capa de rondas hídricas
            
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
            with open('{}/readme.txt'.format(rivers_path), 'w+') as opened_file:
                opened_file.write(self.readme)
            rivers.to_file("{}/{}.shp".format(rivers_path, name))
            
            zip_rivers = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #Se comprimen todos los archivos en el directorio dado
            self.zipdir(rivers_path, zip_rivers)
            zip_rivers.close()

            shutil.rmtree(rivers_path)
            rivers.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            

            list_file.append((label, name))

        if builds is not None:
            label = "Capa de construcciones"
            name = "{}builds_layer".format(self.date)
            builds_path = "{}/{}".format(self.path, name)
            os.mkdir(builds_path)
            with open('{}/readme.txt'.format(builds_path), 'w+') as opened_file:
                opened_file.write(self.readme)
            builds.to_file("{}/{}.shp".format(builds_path, name))
            zip_builds = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

            #Se comprimen todos los archivos en el directorio dado
            self.zipdir(builds_path, zip_builds)
            zip_builds.close()
            shutil.rmtree(builds_path)
            builds.to_file("{}/{}.geojson".format(self.path, name), driver = 'GeoJSON')
            
            list_file.append((label, name))
        if roi is not None:
            label = "Capa de rondas hídricas"
            name = "{}roi_layer".format(self.date)

            rois_path = "{}/{}".format(self.path, name)
           
            os.mkdir(rois_path)
            with open('{}/readme.txt'.format(rois_path), 'w+') as opened_file:
                opened_file.write(self.readme)
            roi.to_file("{}/{}.shp".format(rois_path, name))
            zip_rois = zipfile.ZipFile('{}/{}.zip'.format(self.path, name), 'w', zipfile.ZIP_DEFLATED)

           #Se comprimen todos los archivos en el directorio dado
            self.zipdir(rois_path, zip_rois)
           
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




