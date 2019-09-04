import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.ops import cascaded_union   
from threading import Thread

from imtools import imtools
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

#needed for implementing the download of files
from flask import Flask, send_from_directory
import os

#import functionality of download
from download_files import Download

#import report generation functionality
from generateReport import Report



#creating the server object for downloading files
server = Flask(__name__)



#create a file path for storing the files that will be downloaded - implementation mostly for production 
FILE_PATH = '/resources/shp_geojson'

#creating the path if doesn't exists
if not os.path.exists(FILE_PATH):
    os.makedirs(FILE_PATH)


@server.route("/download/<path:file>")
def download(file):
    return send_from_directory(FILE_PATH, file, as_attachment=True)





colors = ['#011f4b','#03396c', '#005b96','#6497b1','#b3cde0']

#Crear objeto georreferenciador
nom = Nominatim(user_agent= 'my-application')

external_stylesheets = [dbc.themes.BOOTSTRAP]
#external_stylesheets = [
#    "https://unpkg.com/tachyons@4.10.0/css/tachyons.min.css"]
app = dash.Dash(server=server   , external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", 
                            "content": "width=device-width, initial-scale=1"} ])
app.title = 'Inundaciones'

#create navbar and set it to fixed
navbar = dbc.Col([
        dbc.Row([
        html.H2("Zonas susceptibles de inundación",
        style = {
            'textAllign': 'center',
            'color': 'white ',
            'margin': 'auto'
        }),

        ]),
        dbc.Row([

        html.P('Herramienta para identificar zonas susceptibles de inundación debido a la cercania con las rondas de los ríos',
        
        style = {
            'textAllign': 'center',
            'color': 'white ',
            'margin': 'auto'

        })
        ])


    ],
    width = 12,
    style = {
        'background': '#6497b1',
        'padding': '15px'
    },
    
    )

#creating the search tab component

tab_search = dbc.Card([
    dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        html.B("Buscador", style={'color':colors[1]})
                    ]),
                    dbc.Row([
                        dbc.Input(id="searchBar", placeholder="Ingrese un lugar de Colombia", type="text"),
                    ]),
                    dbc.Row([
                        dbc.Button('Buscar', id= 'b_search', style = {"margin-top": "4px", "background": "#6497b1"})
                    ]),
                    dbc.Row([
                        html.B('Fuente:', style={'color':colors[1]})
                        ]),
                    dbc.Row([
                        dcc.Dropdown(id= 'sel_src',
                                        options=[{'label':'OpenSteetMap','value':'osm'},
                                                {'label':'Análisis de Imagen','value':'image'},
                                                {'label': 'Capa de ríos','value':'rios'}],
                                        value= 'osm',
                                        placeholder= 'OpenStreetMap',
                                        style = {
                                            "width": "100%"
                                        }
                                        ),
                    ]),
                ],
                lg = 7,
                style = {
                    "margin-right": "3px",
                    'margin-left': "15px" 
                }),
                dbc.Col([
                    dbc.Row([
                        html.B('Franja de susceptibilidad (metros)')
                    ]),
                    dbc.Row([
                        html.B("Afluentes principales: ", style={'color': colors[2] })
                    ]),
                    dbc.Row([
                        dbc.Input(id = 'i_buffer1', value= '30')
                    ],
                    style = {
                        "width" : "70px" 
                    },
                    justify = "center"
                    
                    ),
                    dbc.Row([
                        html.B("Afluentes secundarios: ", style={'color': colors[2] })
                    ]),
                    dbc.Row([
                        dbc.Input(id = 'i_buffer2', value= '10')
                    ],
                    style = {
                        "width" : "70px" 
                    },
                    ),
                   
                ],
                style = {
                    "margin-left": "15px"
                },
                id = 'buffer',
                lg = 4 )
            ],
            justify="between",),

        dbc.Row([

            dbc.Col([
                    html.B('Coordenadas:', style={'color':colors[1]}),
                    dbc.Col([
                        dbc.Row([
                        html.P("Latitud 1"), 
                        html.P("Longitud 1"),
                        html.P("Latitud 2"),
                        html.P("Longitud 2"),
                        ],
                        justify = "between"),

                        dbc.Row([
                        dbc.Input(id = 'e_lat1', value = 1.153, style={"width": "20%"}), 
                        dbc.Input(id = 'e_lng1', value = -76.656, style={"width": "20%"}),
                        dbc.Input(id = 'e_lat2', value = 1.14, style={"width": "20%"}),
                        dbc.Input(id = 'e_lng2', value = -76.64, style={"width": "20%"})
                        ],
                        justify = "between"),

                         dbc.Row([
                        dbc.Button('Analizar', id= 'b_analizar',  style = {"margin-top": "4px", "background": "#6497b1"})
                        ])
                    ])
                ],
                ),

        ])
    ])

])


#creating the download tab component


tab_download = dbc.Card([

    dbc.CardBody([

    ],
    id = 'download_div' 
    )
])


tabs = dbc.Tabs([
    dbc.Tab(tab_search, label = "Datos"),
    dbc.Tab(tab_download, label = "Descarga")
])


geovisor = dbc.Col([
    dbc.Row([html.B('Geovisor')]),
    dbc.Row([
        html.Iframe(id= 'map', 
                      srcDoc = open('temp.html','r').read(),
                      width= '100%', 
                      height= '540')
    ])

])

#creating the results card for display the graphics
results_card = dbc.Card([

    dbc.CardBody([
        dbc.Col([
            dbc.Row([

            html.H3('Resultados del Análisis',
                               style = {'textAlign':'center',
                                        'color':colors[1]}),
            ]),

            dbc.Row([
            dcc.Graph(id= 'graph_1', style = {'width':'355px',
                                                        'height': '385px'}) 
            ],
            justify = "center"),

            dbc.Row([
            html.H1(html.B('1.012'), id = 'result1_0', style={
                                    'textAlign':'center',
                                       'color':colors[2],
                                       }),
            ],
            justify = "center"),
            dbc.Row([

            html.P('Construcciones dentro de la zona de suceptibilidad',
             style={
                'textAlign':'center',
                'color':colors[3],
                'fontSize':'26px',
                'height':'31px',
                'margin-bottom': '20px'}
            ),      
            ]),
            dbc.Row([

            html.H1(html.B('#####'), id = 'result1_1',
                        style={'textAlign':'center',
                               'color':colors[2],
                               'margin-top': '40px'
                              }), 
            ],
            justify = "center"),

            dbc.Row([
            html.P("Porcentaje", 
            style = {
                'textAlign':'center',
                'color':colors[3],
                'fontSize':'26px',
                'height': '31px'
            }
            ),

            ],
            justify = "center"),

            dbc.Row([
           dcc.Graph(id= 'graph_2', config={'displayModeBar': False},  style = {'width':'330px',
                                                                                'height':'300px',
                                                                                }),  
            ],
            justify = "center"),
            dbc.Row([

           html.H1(html.B('### Hectareas'), id = 'result2_0',
                                   style={'position':'relative',
                                          'textAlign':'center',
                                          'color':colors[2],
                                          }),
            ],
            justify = "center"),

            dbc.Row([
            html.P('dentro de zona susceptible',
                                     style={'textAlign':'center',
                                            'color':colors[3],
                                            'fontSize':'26px',
                                            })                       

            ],
            justify = "center"),

            dbc.Row([
                dbc.Button("Descargar Reporte", style = {
                    'background': '#011f4b',
                    'color': 'white'
                }, id = "report_button")
            ],
            justify = 'center')
        ],
        id = 'dash_board',)
    ])

])



results_tab = dbc.Tabs([

    dbc.Tab(results_card, label = "Resultados")

])





#create a variable to store all the elements before sending it to the dash layout
avant_layout = dbc.Row([
    #column of data input, buttons, map and coordinates
    dbc.Col([
        tabs,
        geovisor,
    
    ],
    #define the sizes of elements in mobile and web
    xl = 7,
    lg = 7,
    md = 7,
    sm = 12,
    xs = 12
    ),

    #column of results
    dbc.Col([
        results_tab
    ],
    xl = 5,
    lg = 5,
    md = 5,
    sm = 12,
    xs = 12
    )


])

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
            'top': '930px',
            'display': 'none'
            }
            )





#hidden div for storing the geojson
hidden_geojson = html.Div(
    id= 'hidden_geojson',
    style={'display':'none',
    'position':'absolute ',
    'top':'990px'}
)

#hidden div for storing the output callback of dataframe
hidden_geodf = html.Div(
    id= 'hidden_geodf',
    style={'display':'none',
    'position':'absolute ',
    'top':'990px'}
)





#hidden div 
hiddenvar = html.Div(children= 'ff',
                     id= 'hidden_var',
                     style={'display':'none',
                            'position':'absolute ',
                            'top':'890px'})


errorMsj = dcc.ConfirmDialog(id = 'error_msj',
                             message = 'Datos no disponibles para esta región',
                             displayed = False)

loading_state = dcc.Loading(id= 'loading', type = 'graph',
                            fullscreen=True)
                
app.layout = html.Div(children = [navbar,
                                  avant_layout,
                                     up_button, 
                                  errorMsj, loading_state,
                                hidden_geojson, hidden_geodf, hiddenvar])


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
     Output(component_id='graph_2', component_property='figure'),
    Output(component_id = 'download_div', component_property = 'children')],
    [Input(component_id='b_search',component_property='n_clicks_timestamp'),
     Input(component_id='b_analizar',component_property='n_clicks_timestamp')],
    [State(component_id='searchBar',component_property='value'),
     State(component_id='sel_src',component_property='value'),
     State(component_id='e_lat1',component_property='value'),
     State(component_id='e_lat2',component_property='value'),
     State(component_id='e_lng1',component_property='value'),
     State(component_id='e_lng2',component_property='value'),
     State(component_id='i_buffer1', component_property='value'),
     State(component_id='i_buffer2', component_property='value')]
)
def detectButton(bnt1, bnt2, str_loc,src_sel, lat1,lat2,lng1,lng2, buffer1, buffer2):
    buffer1 = int(buffer1)
    buffer2 = int(buffer2)

    d_object = Download(FILE_PATH)
    default = d_object.download_file()
    if bnt1 is None and bnt2 is None:
        location = (4.5975, -74.0765)
        Map(location= location, zoom= 15).generateMap()
        #############################  RESULT  ####################################
        figure1 = {'data':[go.Pie(visible=False)]}
        figure2 = {'data':[go.Pie(visible=False)]}
        return ['Inicia ', False, ' ', html.Div(' '),{'visibility':'hidden'},
                '', '','', figure1,figure2, default]
    if bnt1 is None:
        bnt1 = 1
    if bnt2 is None:
        bnt2 = 0
    #El boton buscar es presionado
    if bnt1>bnt2:
        if str_loc == None:
            location = (4.5975, -74.0765)
            Map(location= location, zoom= 15).generateMap()
            #############################  RESULT  #####################################
            figure1 = {'data':[go.Pie(visible=False)]}
            figure2 = {'data':[go.Pie(visible=False)]}
            
            return ['buscar', False, ' ', html.Div(' '), {'visibility':'hidden'},
                    '', '','', figure1, figure2, default]
        else:
            try:
                response = nom.geocode(str_loc +', Colombia')
                lat,lng = response[1]
                location = (lat,lng)
                Map(location= location, zoom= 15).generateMap()
                #############################  RESULT  #####################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['buscar', False, ' ', html.Div(' '), {'visibility':'hidden'},
                        '', '','', figure1, figure2, default]
            except:
                #####################################  RESULT  ##################################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['reintentar', True, 'Error de conexión', html.Div(' '),{'visibility':'hidden'},
                        '','','',figure1, figure2, default]

    else:

        try:
            location = ((float(lat1)+float(lat2))*.5, (float(lng1)+float(lng2))*.5)
        except:
            #####################################  RESULT  ######################################
            figure1 = {'data':[go.Pie(visible=False)]}
            figure2 = {'data':[go.Pie(visible=False)]}
            return ['', True, 'Existen campos vacíos o erróneos en los campos de entrada.', html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2, default]
            
        box_coords = (float(lat2),float(lng1),float(lat1),float(lng2))
        osm = OSMDownloader(box = box_coords)
        ######################     análisis por OpenStreetMap     ###########################
        if src_sel == 'None' or src_sel=='osm': 
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
                Map(location= location, zoom= 15).generateMap()
                ################################  RESULTS #########################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['No hay información disponible', True, msj, html.Div(' '),
                        {'visibility':'hidden'},'','','', figure1, figure2, default]
            else:
                builds = osm._builds.to_crs({'init':'epsg:32618'})
                if type(osm._rivers) is not int:
                    rivers = osm._rivers.to_crs({'init':'epsg:32618'})
                    rivers.geometry = [r.buffer(2*buffer1) if w=='river' else r.buffer(2*buffer2) 
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
                                                            geometry = 'geometry', crs = poly_rivers.crs)
                        except:
                            poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                            geometry = 'geometry', 
                                                            crs = poly_rivers.crs, index = [0])
                        poly_rivers.geometry = poly_rivers.buffer(2*buffer1)
                          
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
                            roi_param = roi.to_crs({'init':'epsg:4326'})
                            Map(location= location, zoom= 15).generateMap(rivers=osm._rivers, 
                                                                          roi = roi_param,
                                                                          bounding = box_coords)
                            download_component = d_object.download_file(rivers = osm._rivers, roi = roi.to_crs({'init':'epsg:4326'} ))

                        else:
                            roi_param = roi.to_crs({'init':'epsg:4326'})
                            build_sus_param = builds_sus.to_crs({'init':'epsg:4326'})
                            Map(location= location, zoom= 15).generateMap(builds = build_sus_param,
                                                                          rivers=osm._rivers, 
                                                                          roi = roi_param,
                                                                          bounding=box_coords)
                            download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param, builds = build_sus_param)

                        
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
                                                    name= 'area fuera de z. susceptible')],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                                      yaxis = go.layout.YAxis(title= 'HECTAREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))
                                }
                        style = {'width':'770px','visibility':'visible'}
                        

                        return ['builds,rivers,poly', False, ' ', html.Div(' '), style,
                                html.B(n_builds_sus), html.B(str(porc_builds)+ ' %'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectareas'),
                                figure1,figure2, download_component ]
                    
                    else:
                        if rivers.shape[0]>1:
                            builds_sus = np.array([builds.geometry.intersects(x) for x in rivers.geometry])
                            builds_sus = builds[np.logical_or.reduce(builds_sus)]
                        else:
                            builds_sus = builds[builds.geometry.intersects(rivers.geometry[0])]
                        
                        if builds_sus.shape[0] == 0:
                            roi_param = rivers.to_crs({'init':'epsg:4326'})
                            Map(location= location, zoom= 15).generateMap(rivers=osm._rivers, 
                                                                          roi = roi_param,
                                                                          bounding=box_coords)
                            download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param)

                        else:
                            build_sus_param = builds_sus.to_crs({'init':'epsg:4326'})
                            roi_param = rivers.to_crs({'init':'epsg:4326'})
                            Map(location= location, zoom= 15).generateMap(builds = build_sus_param,
                                                                          rivers=osm._rivers, 
                                                                          roi = roi_param,
                                                                          bounding=box_coords)   
                            download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param, builds = build_sus_param)

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
                                                    name= 'area fuera de z. susceptible')],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                                      yaxis = go.layout.YAxis(title= 'HECTAREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))}
                        style = {'width':'770px' ,'visibility':'visible'}
                        return ['builds,rivers', False, ' ', html.Div(' '), style,
                                html.B(n_builds_sus), html.B(str(porc_builds)+ ' %'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectareas'),
                                figure1,figure2, download_component]
                else:
                    Map(location= location, zoom= 15).generateMap()
                    msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default]
						
        elif src_sel == 'rios':
            #obtencion capa de rios
            t1 = Thread(target=osm.getRiversLayer)
            t1.start()
            t2 = Thread(target=osm.getRiversPolygons)   
            t2.start()
            t1.join()
            t2.join()
            rivers = None	
            poly_rivers = None	
            if type(osm._rivers) is not int:
                rivers= osm._rivers.to_crs({'init':'epsg:32618'})
                rivers.geometry = [r.buffer(2*buffer1) if w=='river' else r.buffer(2*buffer2) 
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
                                                        geometry = 'geometry', crs = poly_rivers.crs)
                    except:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                        geometry = 'geometry', 
                                                        crs = poly_rivers.crs, index = [0])
                    poly_rivers.geometry = poly_rivers.buffer(2*buffer1)
                    try:      
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs)
                    except:
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs, index = [0])
                    roi_param = roi.to_crs({'init':'epsg:4326'})
                    Map(location= location, zoom= 15).generateMap(rivers=osm._rivers,
                                                                  poly_rivers = osm._poly_rivers,
                                                                  roi = roi_param,
                                                                  bounding=box_coords)
                    #TODO: unir poly_rivers y rivers
                    #FIXME: revisar si builds en verdad va ahi
                    download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param)

                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['rivers, poly', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2, download_component]
                else:
                    roi_param  = roi.to_crs({'init':'epsg:4326'} )
                    download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param )

                    Map(location= location, zoom= 15).generateMap(rivers=osm._rivers,
                                                                  roi = roi_param,
                                                                  bounding=box_coords)
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['rivers', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2, download_component]
            else:
                Map(location= location, zoom= 15).generateMap()
                msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default]
            
        else:
            proj = 'epsg:32618'
            box_google = (float(lat1),float(lng1),float(lat2),float(lng2))
            # objecto de google maps para descarga de imagen satelital 
            gmd = GoogleMapDownloader(coords = box_google, proj=proj)
            ntiles = gmd.computeNtiles()
            #tamano permitido de región de análisis
            if ntiles > 256:
                ###########################  RESULTS  ####################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                msj = 'La región de análisis es muy grande, por favor intente con una más pequeña!'
                return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2, default]
            
            #Si la región cumple el tamaño de análisis permitido
            #descarga de información de OSMDownloader
            t1 = Thread(target=osm.getRiversLayer)
            t1.start()
            t2 = Thread(target=osm.getRiversPolygons)   
            t2.start()
            t1.join()
            t2.join()
            rivers = None	
            poly_rivers = None
            #hay información de capas de rios
            if type(osm._rivers) is not int:
                #Generando imagen satelital de la region de analisis 
                try:
                    img = np.array(gmd.generateImage(), dtype = np.uint8)
                except:
                    ###########################  RESULTS  ####################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    msj = 'No se puede realizar el análisis por imagenes satelitales, revise las coordenadas!'
                    return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                        '','','',figure1,figure2, default]
                
                #generando region de analisis en la imagen
                analysis_region = osm.computeROIsuperpixels(buffer1)
                
                ## mask image and superpixel computing
                out, m = imtools.maskRasterIm(img, gmd.GT, analysis_region)
                segments = imtools.computeSegments(out,mask=m) 
                
                ### aqui modelo de clasificacicón de la imagen  ###
                ###################################################
                ###################################################
                    
                ## mapeando los segmentos al mapa de dash  
                seg_polygons = imtools.mapSuperPixels(segments=segments, GT=gmd.GT, verbose=False)
                #generando buffer de rios
                rivers= osm._rivers.to_crs({'init':'epsg:32618'})
                rivers.geometry = [r.buffer(2*buffer1) if w=='river' else r.buffer(2*buffer2) 
                                   for r, w in zip(rivers.geometry,rivers['waterway'])]
                try:
                    rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                               geometry = 'geometry',
                                               crs =rivers.crs)
                except:
                    rivers = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.geometry)},
                                               geometry = 'geometry',
                                               crs =rivers.crs, index = [0])
                #hay informacion de polygonos de rios                               
                if type(osm._poly_rivers) is not int:
                    poly_rivers = osm._poly_rivers.to_crs({'init':'epsg:32618'})
                    try:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                        geometry='geometry', crs = poly_rivers.crs)
                    except:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.geometry)},
                                                        geometry='geometry', 
                                                        crs = poly_rivers.crs, index = [0])
                    poly_rivers.geometry = poly_rivers.buffer(2*buffer1)
                    
                    #### generando ROI (región de análisis)
                    try:      
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs)
                    except:
                        roi = gpd.GeoDataFrame({'geometry':cascaded_union(rivers.union(poly_rivers))},
                                                geometry = 'geometry', 
                                                crs = rivers.crs, index = [0])
                    
                    roi_params = roi.to_crs({'init':'epsg:4326'})
                    superpixels_params = seg_polygons.to_crs(crs={'init':'epsg:4326'})

                    Map(location= location, zoom= 15).generateMap(rivers=osm._rivers,
                                                                  poly_rivers = osm._poly_rivers,
                                                                  roi = roi_params,
                                                                  superpixels= superpixels_params,
                                                                  bounding=box_coords)
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    #TODO unir tivers y polyrivers
                    download_component = d_object.download_file(rivers = osm._rivers, builds = superpixels_params, roi = roi_params)
                    return ['rivers, poly, superpixels', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2, download_component]
                            
                else:

                    roi_params = rivers.to_crs({'init':'epsg:4326'})
                    superpixels_params = seg_polygons.to_crs({'init':'epsg:4326'})
                    Map(location= location, zoom= 15).generateMap(rivers=osm._rivers,
                                                                  roi = roi_params,
                                                                  superpixels= superpixels_params,
                                                                  bounding=box_coords)
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    download_component = d_object.download_file(rivers = osm._rivers, builds = superpixels_params, roi = roi_params)
                    return ['rivers, superpixels', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2, download_component]
            #No hay informacion de capas de rios, por ende no se genera imagen satelital
            else:
                Map(location= location, zoom= 15).generateMap()
                msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default]   

@app.callback(
        Output(component_id= 'map', component_property = 'srcDoc'),
         #Output(component_id= 'error_msj',component_property = 'message')],
        [Input(component_id= 'hidden_var',component_property = 'children')]
)
def update_map(value):
    return open('temp.html','r').read()



#callback for upload a shapefile
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
            children= 'Ha habido un error en la carga del archivo',
            style = {
                'color' : 'red'
            }
            )
    else:
        return None

#callback for create a geodataframe and put it on map
@app.callback(
    Output ('hidden_geodf', 'children'),
    [Input ('hidden_geojson', 'children')]
)
def assign_geodf(geojson):
    if geojson is not None:

        geo_df = gpd.read_file(geojson)
        print("dataframe: {}".format(type(geo_df)))
        print(geo_df['geometry'])







#start aplication 
if __name__ == '__main__':
    app.run_server(debug=True)