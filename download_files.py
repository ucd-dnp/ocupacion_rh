
#needed libraries for create component
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import geopandas as gpd



class Download:

    def __init__(self, path):
        self.path = path
    

    def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
        location = "/download/{}".format(urlquote(filename))
        return html.A(filename, href=location)

    def download_file (self, rivers = None, builds = None, roi = None ):
        list_file = []
        if rivers is not None:
            label = "Capa de rios"
            name = "rivers_layer"
            gpd.to_file("{}/{}.shp".format(path, name))
            gpd.to_file("{}/{}.geojson".format(path, name), driver = "geojson")
            
            list_file.append((label, name))
        if builds is not None:
            label = "Capa de construcciones"
            name = "builds_layer"
            gpd.to_file("{}/{}.shp".format(path, name))
            gpd.to_file("{}/{}.geojson".format(path, name), driver = "geojson")
            
            list_file.append((label, name))
        if roi is not None:
            label = "Capa de regiones"
            name = "roi_layer"
            gpd.to_file("{}/{}.shp".format(path, name))
            gpd.to_file("{}/{}.geojson".format(path, name), driver = "geojson")

            list_file.append((label, name))

        #create the component to be returned    
        download_component = dbc.Container([
            html.Label("Seleccione cual de los siguientes archivos quiere descargar"),
            dbc.Row([
                    if !list_file:
                        html.Label("No se encuentran capas para descargar")
                    else:
                        #creating download links with existing layers
                        for i in range(len(list_file)):
                            dbc.Col([
                                html.H3(list_file[i][0])
                                link_name = list_file[i][1]
                                file_download_link(link_name.join(".shp"))
                                file_download_link(link_name.join(".geojson"))
                            ])
            ])


        ])
        return download_component




