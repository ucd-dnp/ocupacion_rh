import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.ops import cascaded_union   
from threading import Thread

from generateMap import Map
from osm_downloader import OSMDownloader
from google_maps_downloader import GoogleMapDownloader

import numpy as np
import plotly.graph_objs as go
#import matplotlib.pyplot as plt

#needed to decode uploaded files
import base64
import io
import fiona

#temporarly libraries
import pandas as pd

colors = ['#011f4b','#03396c', '#005b96','#6497b1','#b3cde0']

#Crear objeto georreferenciador
nom = Nominatim(user_agent='my-application')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets = [
#    "https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", 
                            "content": "width=device-width, initial-scale=1"} ])
app.title = 'Inundaciones'

title = html.H1('Zonas susceptibles de inundación',
                style={'textAlign': 'center',
                       'color': colors[1]})

intro = html.Div('Herramienta para identificar zonas susceptibles de inundación debido a la cercania con las rondas de los ríos',
                 style={'textAlign': 'center',
                        'color': colors[2]})


#search bar objects
search_bar = html.Div([html.Label(html.B('Buscador:', style={'color':colors[1]})),
                    dcc.Input(id='searchBar', 
                              placeholder='Search..',
                              type='text',
                              style={'position':'relative',
                                     'width':'198px'}),
                    html.Button('Buscar', id= 'b_search', type = 'submit',
                                style = {'position':'relative',
                                         'left':'10px',
                                         'width':'127px'})],
                      style = {'position':'absolute',
                               'top':'110px',
                               'left':'6px'})
#seleccion de fuente de datos
srcData = html.Div([html.Label(html.B('Fuente:', style={'color':colors[1]})),
                    dcc.Dropdown(id='sel_src',
                            options=[{'label':'OpenSteetMap','value':'osm'},
                                     {'label':'Análisis de Imagen','value':'image'},
                                     {'label': 'Capa de ríos','value':'rios'}],
                            value='osm',
                            placeholder='OpenStreetMap',
                            style={'position':'relative',
                                   'width':'198px',
                                   'height':'38px'}),
                    html.Button('Analizar', id = 'b_analizar', type = 'submit',
                                style = {'position': 'relative',
                                         'width': '127px',
                                         'top': '-38px',
                                         'left':'208px'})],
                    style = {'position':'absolute',
                             'top':'175px',
                             'left':'6px'})

#upload shapefile button
up_button = html.Div([
   dcc.Markdown('''
    Por favor seleccione un archivo
    '''),
     dcc.Upload(
        id = 'upload-data',
        children = html.Button('Cargar', id = 's_button'),
        accept = '.geojson'
    )
    ],
    style ={'position':'absolute',
            'width': '48%',
            'top': '930px'
            }
            )

#hidden div for storing the geojson
hidden_geojson = html.Div(
    children = "{'juan': 12}",
    id='hidden_geojson',
    style={'display':'none',
    'position':'absolute ',
    'top':'990px'}
)

hidden_geodf = html.Div(
    children = "ff",
    id='hidden_geodf',
    style={'display':'none',
    'position':'absolute ',
    'top':'990px'}
)


#geovisor object to show the results
geovisor= html.Div([html.Div([html.B('Geovisor')]),
                    html.Iframe(id='map', 
                      srcDoc = open('temp.html','r').read(),
                      width='100%', 
                      height='540')],
                    style= {'position':'absolute',
                            'top':'240px',
                            'width':'700px'})

#Franja de susceptibilidad
slider = html.Div([html.Label('Franja de susceptibilidad (metros)'),
                   dcc.Slider(min=30, max = 300,value=30,
                              marks={30:'min:30',300:'max:300',70:'70',
                                     100:'100',150:'150',200:'200',250:'250'},
                              id='s_slider'),
                   dcc.Input(id = 'i_buffer', value= '30',
                             style = {'width':'51px',
                                      'position':'relative',
                                      'top':'-32px',
                                      'left': '240px',
                                      'textAlign':'center'})],
                style={'position':'absolute',
                       'left':'400px',
                       'top': 150},
                id = 'buffer')
#Textos
aux_text = html.Div('Enter a value and press submit',
                    id='text1')
t_lat1 = html.Div('Latitud 1',
                id = 't_lat1',
                style={'position':'absolute',
                       'left':'10px',
                       'top':'810px',
                       'width':'80px',
                       'textAlign':'center'})
t_lng1 = html.Div('Longitud 1',
                id = 't_lng1',
                style={'position':'absolute',
                       'left':'110px',
                       'top':'810px',
                       'width':'80px',
                       'textAlign':'center'})
t_lat2 = html.Div('Latitud 2',
                id = 't_lat2',
                style={'position':'absolute',
                       'left':'210px',
                       'top':'810px',
                       'width':'80px',
                       'textAlign':'center'})
t_lng2 = html.Div('Longitud 2',
                id = 't_lng2',
                style={'position':'absolute',
                       'left':'310px',
                       'top':'810px',
                       'width':'80px',
                       'textAlign':'center'})

lat1 = dcc.Input(id = 'e_lat1',
                   style={'position':'absolute',
                       'left':'10px',
                       'top':'840px',
                       'width':'80px'})
lng1 = dcc.Input(id = 'e_lng1',
                   style={'position':'absolute',
                       'left':'110px',
                       'top':'840px',
                       'width':'80px'})
lat2 = dcc.Input(id = 'e_lat2',
                   style={'position':'absolute',
                       'left':'210px',
                       'top':'840px',
                       'width':'80px'})
lng2 = dcc.Input(id = 'e_lng2',
                   style={'position':'absolute',
                       'left':'310px',
                       'top':'840px',
                       'width':'80px'})

coords = html.Div([t_lat1, t_lng1, t_lat2, t_lng2,
                   lat1,lng1,lat2,lng2])

#hidden div 
hiddenvar = html.Div(children='ff',
                     id='hidden_var',
                     style={'visibility':'visible',
                            'position':'absolute ',
                            'top':'890px'})
# contairner de resultados
dashboard =  html.Div([html.H3('Resultados del Análisis',
                               style = {'textAlign':'center',
                                        'color':colors[1]}),
                       dcc.Graph(id='graph_1', style = {'width':'385px',
                                                        'height': '385px'}),
                    html.Div([
                       html.H1(html.B('1.012'), id = 'result1_0',
                               style={'position':'relative',
                                      'textAlign':'center',
                                      'color':colors[2],
                                      'margin-bottom':'5px'}),
                       html.Div('construcciones dentro',
                               style={'position':'relative',
                                      'textAlign':'center',
                                      'color':colors[3],
                                      'fontSize':'26px',
                                      'height': '31px'}),
                       html.Div('de la zona de susceptibilidad',
                               style={'textAlign':'center',
                                      'color':colors[3],
                                      'fontSize':'26px',
                                      'height':'31px'}),
                      html.H1(html.B('#####'), id = 'result1_1',
                               style={'textAlign':'center',
                                      'color':colors[2],
                                      'margin-bottom':'0px',
                                      'margin-top': '25px'}),
                      html.Div('porcentaje',
                               style={'textAlign':'center',
                                      'color':colors[3],
                                      'fontSize':'26px',
                                      'height': '31px'})],
                                style ={'position':'relative',
                                        'width': '48%',
                                        'top':'-320px',
                                        'left':'396px'}),
                         dcc.Graph(id= 'graph_2', style = {'width':'300px',
                                                           'height':'300px',
                                                           'position':'relative',
                                                           'top':'-220px'},
                                    config={'displayModeBar': False}),
                   html.Div([
                           html.H1(html.B('### Hectareas'), id = 'result2_0',
                                   style={'position':'relative',
                                          'textAlign':'center',
                                          'color':colors[2],
                                          'margin-bottom':'5px'}),
                           html.Div('dentro de zona susceptible',
                                     style={'textAlign':'center',
                                            'color':colors[3],
                                            'fontSize':'26px',
                                            'height':'31px'})],
                           style ={'position':'relative',
                                        'width': '48%',
                                        'top':'-400px',
                                        'left':'396px'}
                           )                                         
                      ],
                       id = 'dash_board',
                       style = {'position':'absolute',
                                'top':'100px',
                                'left':'630px',
                                'width':'770px',
                                'visibility':'hidden'}
                     )



errorMsj = dcc.ConfirmDialog(id = 'error_msj',
                             message = 'Datos no disponibles para esta región',
                             displayed = False)

loading_state = dcc.Loading(id='loading', type = 'graph',
                            fullscreen=True)
                

app.layout = html.Div(children = [title, intro,
                                  search_bar,
                                  srcData,
                                  geovisor,
                                  coords, up_button, slider,
                                  hiddenvar, errorMsj, loading_state,
                                  dashboard, hidden_geojson, hidden_geodf])


@app.callback(
    [Output(component_id='hidden_var',component_property='children'),
     Output(component_id='error_msj', component_property='displayed'),
     Output(component_id='error_msj',component_property='message'),
     Output(component_id= 'loading', component_property = 'children'),
     Output(component_id='dash_board',component_property='style'),
	 Output(component_id='result1_0',component_property='children'),
     Output(component_id='result1_1',component_property='children'),
     Output(component_id='result2_0',component_property='children'),
     Output(component_id='graph_1', component_property='figure'),
     Output(component_id='graph_2', component_property='figure')],
    [Input(component_id='b_search',component_property='n_clicks_timestamp'),
     Input(component_id='b_analizar',component_property='n_clicks_timestamp')],
    [State(component_id='searchBar',component_property='value'),
     State(component_id='sel_src',component_property='value'),
     State(component_id='e_lat1',component_property='value'),
     State(component_id='e_lat2',component_property='value'),
     State(component_id='e_lng1',component_property='value'),
     State(component_id='e_lng2',component_property='value'),
     State(component_id='s_slider', component_property='value')]
)
def detectButton(bnt1, bnt2, str_loc,src_sel, lat1,lat2,lng1,lng2, buffer):
     
    if bnt1 is None and bnt2 is None:
        location = (4.5975, -74.0765)
        Map(location= location, zoom= 13).generateMap()
        #############################  RESULT  ####################################
        figure1 = {'data':[go.Pie(visible=False)]}
        figure2 = {'data':[go.Pie(visible=False)]}
        return ['Inicia ', False, ' ', html.Div(' '),{'visibility':'hidden'},
                '', '','', figure1,figure2]
    if bnt1 is None:
        bnt1 = 1
    if bnt2 is None:
        bnt2 = 0
    if bnt1>bnt2:
        if str_loc == None:
            location = (4.5975, -74.0765)
            Map(location= location, zoom= 13).generateMap()
            #############################  RESULT  #####################################
            figure1 = {'data':[go.Pie(visible=False)]}
            figure2 = {'data':[go.Pie(visible=False)]}
            return ['buscar', False, ' ', html.Div(' '), {'visibility':'hidden'},
                    '', '','', figure1, figure2]
        else:
            try:
                response = nom.geocode(str_loc +', Colombia')
                lat,lng = response[1]
                location = (lat,lng)
                Map(location= location, zoom= 13).generateMap()
                #############################  RESULT  #####################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['buscar', False, ' ', html.Div(' '), {'visibility':'hidden'},
                        '', '','', figure1, figure2]
            except:
                #####################################  RESULT  ##################################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['reintentar', True, 'Error de conexión', html.Div(' '),{'visibility':'hidden'},
                        '','','',figure1, figure2]

    else:

        try:
            location = ((float(lat1)+float(lat2))*.5, (float(lng1)+float(lng2))*.5)
        except:
            #####################################  RESULT  ######################################
            figure1 = {'data':[go.Pie(visible=False)]}
            figure2 = {'data':[go.Pie(visible=False)]}
            return ['', True, 'Existen campos vacíos o erróneos en los campos de entrada.', html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2]
            
        box_coords = (float(lat2),float(lng1),float(lat1),float(lng2))
        if src_sel == 'None' or src_sel=='osm':
            osm = OSMDownloader(box = box_coords)
            
            t1 = Thread(target=osm.getBuildings)
            t1.start()
            t2 = Thread(target=osm.getRiversLayer)
            t2.start()
            t3 = Thread(target=osm.getRiversPolygons)   
            t3.start()
            t1.join()
            t2.join()
            t3.join()
            
            if type(osm._builds) is int:
                msj = """No hay información disponible de construcciones para esta región. 
Intente con otra región o cambie la fuente de análisis por
'Análisis de imagen'"""
                Map(location= location, zoom= 13).generateMap()
                ################################  RESULTS #########################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['No hay información disponible', True, msj, html.Div(' '),
                        {'visibility':'hidden'},'','','', figure1, figure2]
            else:
                builds = osm._builds.to_crs({'init':'epsg:32618'})
                if type(osm._rivers) is not int:
                    rivers = osm._rivers.to_crs({'init':'epsg:32618'})
                    rivers.geometry = [r.buffer(2*buffer) if w=='river' else r.buffer(2*buffer*0.4) 
                                    for r, w in zip(rivers.geometry,rivers['waterway'])]
                    try:
                        rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                                   geometry = 'geometry',
                                                   crs =rivers.crs)
                    except:
                        rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                                   geometry = 'geometry',
                                                   crs =rivers.crs, index = [0])
                    if type(osm._poly_rivers) is not int:
                        poly_rivers = osm._poly_rivers.to_crs({'init':'epsg:32618'})
                        try:
                            poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                            geometry='geometry', crs = poly_rivers.crs)
                        except:
                            poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                            geometry='geometry', 
                                                            crs = poly_rivers.crs, index = [0])
                        poly_rivers.geometry = poly_rivers.buffer(2*buffer)
                          
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs)
                        
                        #Calculando en numero de construcciones que intersectan la zona de susceptibles
                        if roi.shape[0] > 1:
                            builds_sus = np.array([builds.geometry.intersects(x) for x in roi.geometry])
                            builds_sus = builds[np.logical_or.reduce(builds_sus)]
                        else:
                            builds_sus = builds[builds.geometry.intersects(roi.geometry[0])]
                        
                        if builds_sus.shape[0] == 0:
                            Map(location= location, zoom= 13).generateMap(rivers=osm._rivers, 
                                                                          roi = roi.to_crs({'init':'epsg:4326'}))
                        else:
                            Map(location= location, zoom= 13).generateMap(builds = builds_sus.to_crs({'init':'epsg:4326'}),
                                                                          rivers=osm._rivers, 
                                                                          roi = roi.to_crs({'init':'epsg:4326'}))
                        
                        ########################################## RESULTS #######################################
                        n_builds = np.shape(osm._builds)[0]
                        n_builds_sus = np.shape(builds_sus)[0]
                        porc_builds = int(100*n_builds_sus/n_builds)
                        total_area = np.sum(builds.area)/10000 # hectareas
                        total_area_sus = np.sum(builds_sus.area)/10000 # hectareas
                        figure1 = {'data': [go.Pie(visible= True, values=[n_builds_sus, n_builds-n_builds_sus],
                                                  labels = ['susceptibles', 'No susceptibles'], hole=0.33)],
                                   'layout':go.Layout(margin=go.layout.Margin(l=10, r=95, t=25, b=1,autoexpand = False))}
                        figure2 = {'data': [go.Bar(visible = True, x = ['AREA'], y = [total_area_sus], 
                                                    name= 'area dentro de z. susceptible'),
                                             go.Bar(visible = True, x= ['AREA'], y = [total_area- total_area_sus], 
                                                    name='area fuera de z. susceptible')],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                                      yaxis = go.layout.YAxis(title='HECTAREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))
                                }
                        style = {'position':'absolute','top':'110px','left':'720px',
                            'width':'770px','height':'790px' ,'visibility':'visible'}
                        
                        return ['builds,rivers,poly', False, ' ', html.Div(' '), style,
                                html.B(n_builds_sus), html.B(str(porc_builds)+ ' %'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectareas'),
                                figure1,figure2]
                    
                    else:
                        if rivers.shape[0]>1:
                            builds_sus = np.array([builds.geometry.intersects(x) for x in rivers.geometry])
                            builds_sus = builds[np.logical_or.reduce(builds_sus)]
                        else:
                            builds_sus = builds[builds.geometry.intersects(rivers.geometry[0])]
                        
                        if builds_sus.shape[0] == 0:
                            Map(location= location, zoom= 13).generateMap(rivers=osm._rivers, 
                                                                          roi = rivers.to_crs({'init':'epsg:4326'}))
                        else:
                            Map(location= location, zoom= 13).generateMap(builds = builds_sus.to_crs({'init':'epsg:4326'}),
                                                                          rivers=osm._rivers, 
                                                                          roi = rivers.to_crs({'init':'epsg:4326'}))   
                        #####################################  RESULTS  ##########################################
                        n_builds = np.shape(osm._builds)[0]
                        n_builds_sus = np.shape(builds_sus)[0]
                        porc_builds = int(100*n_builds_sus/n_builds)
                        total_area = np.sum(builds.area)/10000 # hectareas
                        total_area_sus = np.sum(builds_sus.area)/10000 # hectareas
                        figure1 = {'data': [go.Pie(visible = True, values=[n_builds_sus, n_builds-n_builds_sus],
                                                  labels = ['susceptibles', 'No susceptibles'])],
                                   'layout': go.Layout(margin=go.layout.Margin(l=10, r=95, t=25, b=1,autoexpand = False))}
                        figure2 = {'data': [go.Bar(visible = True, x = ['AREA'], y = [total_area_sus], 
                                                    name= 'area dentro de z. susceptible'),
                                             go.Bar(visible = True, x= ['AREA'], y = [total_area- total_area_sus], 
                                                    name='area fuera de z. susceptible')],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                                      yaxis = go.layout.YAxis(title='HECTAREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))}
                        style = {'position':'absolute','top':'110px','left':'720px',
                            'width':'770px','height':'790px' ,'visibility':'visible'}
                        return ['builds,rivers', False, ' ', html.Div(' '), style,
                                html.B(n_builds_sus), html.B(str(porc_builds)+ ' %'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectareas'),
                                figure1,figure2]
                else:
                    Map(location= location, zoom= 13).generateMap()
                    msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2]
						
        elif src_sel == 'rios':
            osm = OSMDownloader(box = box_coords)
            #obtencion capa de rios
            t2 = Thread(target=osm.getRiversLayer)
            t2.start()
            t3 = Thread(target=osm.getRiversPolygons)   
            t3.start()
            t2.join()
            t3.join()
            rivers = None	
            poly_rivers = None	
            if type(osm._rivers) is not int:
                rivers= osm._rivers.to_crs({'init':'epsg:32618'})
                rivers.geometry = [r.buffer(2*buffer) if w=='river' else r.buffer(2*buffer*0.4) 
                                   for r, w in zip(rivers.geometry,rivers['waterway'])]
                try:
                    rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                               geometry = 'geometry',
                                               crs =rivers.crs)
                except:
                    rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                               geometry = 'geometry',
                                               crs =rivers.crs, index = [0])
                if type(osm._poly_rivers) is not int:
                    poly_rivers = osm._poly_rivers.to_crs({'init':'epsg:32618'})
                    try:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                        geometry='geometry', crs = poly_rivers.crs)
                    except:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                        geometry='geometry', 
                                                        crs = poly_rivers.crs, index = [0])
                    poly_rivers.geometry = poly_rivers.buffer(2*buffer)
                    try:      
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs)
                    except:
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs, index = [0])
                    Map(location= location, zoom= 13).generateMap(rivers=osm._rivers,
                                                                  poly_rivers = osm._poly_rivers,
                                                                  roi = roi.to_crs({'init':'epsg:4326'}))
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['rivers, poly', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2]
                else:
                    Map(location= location, zoom= 13).generateMap(rivers=osm._rivers,
                                                                  roi = rivers.to_crs({'init':'epsg:4326'}))
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['rivers', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2]
            else:
                Map(location= location, zoom= 13).generateMap()
                msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2]
            
        else:
            box_google = (float(lat1),float(lng1),float(lat2),float(lng2))
            proj = 'epsg:32618'
            gmd = GoogleMapDownloader(coords = box_google, proj=proj)
            ntiles = gmd.computeNtiles()
            if ntiles <= 255:
                try:
                    im = np.array(gmd.generateImage())
                    gmd.save_raster(im,'prueba.tif')
                    ###########################  RESULTS  ####################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    msj = 'La región de análisis es muy grande, por favor intente con una más pequeña!'
                    return ['imagen generada', False, msj, html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2]
                except IOError:
                    ###########################  RESULTS  ####################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    msj = 'No se pudo completar análisis, intente de nuevo.'
                    return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                        '','','',figure1,figure2]
            else:
                ###########################  RESULTS  ####################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                msj = 'La región de análisis es muy grande, por favor intente con una más pequeña!'
                return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2]

@app.callback(
        Output(component_id='map', component_property='srcDoc'),
         #Output(component_id='error_msj',component_property='message')],
        [Input(component_id='hidden_var',component_property='children')]
)
def update_map(value):
    return open('temp.html','r').read()

@app.callback(
        Output(component_id='s_slider',component_property='value'),
        [Input(component_id='i_buffer', component_property = 'value')])
def update_slider(value):
    try:
        v = int(value)
        if v<30:
            v = 30
        elif v>300:
            v = 300
    except:
        v = 30
    return v


#callback for upload a geojson and storing it on a hidden div
@app.callback(
    Output('hidden_geojson', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def set_shapefile(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'geojson' in filename:
                data_decoded = decoded.decode('ISO-8859-1')
                #return the json object
                return data_decoded
            else:
                raise Exception("wrong input file")
        except Exception as e:
            print("Error: {}".format(e))

            return  html.H5(
            id = 'error_message',
            children='Ha habido un error en la carga del archivo',
            style = {
                'color' : 'red'
            }
            )

#callback for create a geodataframe and put it on map
@app.callback(
    Output ('hidden_geodf', 'children'),
    [Input ('hidden_geojson', 'children')]
)
def assign_geodf(geojson):
    geo_df = gpd.read_file(geojson)
    print("dataframe: {}".format(type(geo_df)))
    print(geo_df['geometry'])


#start aplication 
if __name__ == '__main__':
    app.run_server(debug=True)