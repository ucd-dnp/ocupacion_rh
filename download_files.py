
#needed libraries for create component
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import geopandas as gpd



class Download:

    def __init__(self, path):
        self.path = path
    
    # def convert_2_geojson (dataframe):
    #     return gpd.GeoSeries([dataframe]).__geo_interface__

    # #for the download button it is needed that file is stored in the "server" directory first
    # def save_file(name, content):
    #     data = content.encode('ISO-8859-1').split(b";base64,")[1]

    #     with open(os.path.join((FILE_PATH), name), 'wb') as fp:
    #         fp.write(base64.decodebytes(data))
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
            
            list_file.append(rivers)
        if builds is not None:
            label = "Capa de construcciones"
            name = "builds_layer"
            gpd.to_file("{}/{}.shp".format(path, name))
            gpd.to_file("{}/{}.geojson".format(path, name), driver = "geojson")
            
            list_file.append(builds)
        if roi is not None:
            label = "Capa de regiones"
            name = "roi_layer"
            gpd.to_file("{}/{}.shp".format(path, name))
            gpd.to_file("{}/{}.geojson".format(path, name), driver = "geojson")

        download_component = html.Div([
            html.Label("Seleccione cual de los siguientes archivos quiere descargar"),
            

        ])
        return




