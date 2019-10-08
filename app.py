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
import cv2
import pickle
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


env_file = open('env_variables.dat', 'r')
envs_names = [line.strip() for line in env_file]

#create a file path for storing the files that will be downloaded - implementation mostly for production 
FILE_PATH = envs_names[1]

REPORT_PATH = envs_names[0]




@server.route("/download/<path:file>")
def download(file):
    return send_from_directory(FILE_PATH, file, as_attachment=True)

@server.route("/report/<path:file>")
def download_report(file):
    print("si entré, pero me jodí")
    print("fiel: {}".format(file))
    print("path: {}".format(REPORT_PATH))
    return send_from_directory(REPORT_PATH, file, as_attachment=True)




colors = ['#011f4b','#03396c', '#005b96','#6497b1','#b3cde0']

graph_colors = ['rgb(255,127,14)', 'rgb(31,119,180)']

#Crear objeto georreferenciador
nom = Nominatim(user_agent= 'my-application1')
# crear objeto de clasificación
pipeline = pickle.load(open('./training/model.p','rb'))

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(server=server   , external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", 
                            "content": "width=device-width, initial-scale=1"} ])



#       .o8                     oooo                                                    oooo         o8o            
#      "888                     `888                                                    `888         `"'            
#  .oooo888   .oooo.    .oooo.o  888 .oo.       .oooooooo oooo d8b  .oooo.   oo.ooooo.   888 .oo.   oooo   .ooooo.  
# d88' `888  `P  )88b  d88(  "8  888P"Y88b     888' `88b  `888""8P `P  )88b   888' `88b  888P"Y88b  `888  d88' `"Y8 
# 888   888   .oP"888  `"Y88b.   888   888     888   888   888      .oP"888   888   888  888   888   888  888       
# 888   888  d8(  888  o.  )88b  888   888     `88bod8P'   888     d8(  888   888   888  888   888   888  888   .o8 
# `Y8bod88P" `Y888""8o 8""888P' o888o o888o    `8oooooo.  d888b    `Y888""8o  888bod8P' o888o o888o o888o `Y8bod8P' 
#                                              d"     YD                      888                                   
#                                              "Y88888P'                     o888o                                  
                                                                                                                  
#           oooo                                                        .            
#           `888                                                      .o8            
#  .ooooo.   888   .ooooo.  ooo. .oo.  .oo.    .ooooo.  ooo. .oo.   .o888oo  .oooo.o 
# d88' `88b  888  d88' `88b `888P"Y88bP"Y88b  d88' `88b `888P"Y88b    888   d88(  "8 
# 888ooo888  888  888ooo888  888   888   888  888ooo888  888   888    888   `"Y88b.  
# 888    .o  888  888    .o  888   888   888  888    .o  888   888    888 . o.  )88b 
# `Y8bod8P' o888o `Y8bod8P' o888o o888o o888o `Y8bod8P' o888o o888o   "888" 8""888P' 

#En esta seccion se crean los elementos que conformarán la vista de la aplicación 
app.title = 'Inundaciones'

navbar = dbc.Col([
        dbc.Row([
        html.H2("Ocupación e infraestructura en zonas de ronda hídrica",
        style = {
            'textAllign': 'center',
            'color': 'white ',
            'margin': 'auto'
        }),

        ]),
        dbc.Row([

        html.P('Herramienta para identificar áreas ocupadas y conteo de infraestructura en zonas de ronda hídrica',
        
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

#Se crea el panel de datos 
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
                        html.B('Ronda Hídrica (metros)')
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
                        
                         dbc.Input(id = 'e_lat1', value =  1.1573, style={"width": "20%"}), 
                         dbc.Input(id = 'e_lng1', value = -76.6590, style={"width": "20%"}),
                         dbc.Input(id = 'e_lat2', value = 1.1355, style={"width": "20%"}),
                         dbc.Input(id = 'e_lng2', value = -76.6312, style={"width": "20%"})
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


#Panel de descarga de archivos
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
    dbc.Row([html.H4('Geovisor')],
    justify = "center"),
    dbc.Row([
        html.Iframe(id= 'map', 
                      srcDoc = open('temp1.html','r').read(),
                      width= '100%', 
                      height= '671')
    ],

    style = {
        "margin-left": "15px"
    })

])


results_card = dbc.Card([
    dbc.CardBody([
        dbc.Col([
            dbc.Row([html.H3('Resultados del Análisis',
                             style = {'textAlign':'center',
                                      'color'    :colors[1]})]
            ),

            dbc.Row([dcc.Graph(id= 'graph_1', 
                               style = {'width' : '385px',
                                        'height': '385px'})],
                    justify = "center"
            ),

            dbc.Row([html.H1(html.B('######'), id = 'result1_0', 
                             style={'textAlign':'center',
                                    'color'    :colors[2]})],
                    justify = "center"
            ),
            
            dbc.Row([html.P ('dentro de la ronda hídrica',
                             style={'textAlign'    : 'center',
                                    'color'        : colors[3],
                                    'fontSize'     : '26px',
                                    'height'       : '31px',
                                    'margin-bottom': '20px'})], 
                    justify = "center"
            ),
            
            dbc.Row([html.H1(html.B('######'), id = 'result1_1',
                             style={'textAlign' : 'center',
                                    'color'     : colors[2],
                                    'margin-top': '40px'})],
                    justify = "center"
            ),

            dbc.Row([dcc.Graph(id= 'graph_2', config={'displayModeBar': False}, 
                              style = {'width' : '385px',
                                       'height': '320px'})],
                    justify = "center"
            ),
            
            dbc.Row([html.H1(html.B('### Hectareas'), id = 'result2_0',
                             style={'position'     : 'relative',
                                    'textAlign'    : 'center',
                                    'margin-bottom': '25px',
                                    'color'        : colors[2]})],
                    justify = "center"
            ),

            dbc.Row([html.P("Generando archivo PDF",
                            style={'textAlign'  :'center',
                                   'color'      : colors[1],
                                   'fontSize'   : '20px',
                                   'font-weight': 'bold'})],
                    justify = 'center',
                    id = 'pdf_text',
                    style = {'display': 'none'}
            ),
            
            dbc.Row([dbc.Spinner(size="lg", color='danger')],
                    justify = "center",
                    id = 'pdf_spinner',
                    style = {'display': 'none'}
            ),

            dbc.Row([dbc.Button("Generar reporte", id = "report_button")],
                    justify = 'center'
            ),

            dbc.Row([dbc.Button([],
                                size = "lg",
                                id = "download_report_button",
                                style = {'display': 'none'})],
                    id = 'download_report',
                    justify = 'center'
            ) 
        ],
        id = 'dash_board',)
    ])
])


# Se añade el panel de resultados dentro de un contenedor (tab)
results_tab = dbc.Tabs([

    dbc.Tab(results_card, label = "Resultados")

])



disclaimer = dbc.Row([
    dbc.Col([
        html.Img(src = './assets/img/warning.ico', width = '50', height = '50')
    ],
    width = 1),
    dbc.Col([

    dcc.Markdown('''Este reporte contiene *información indicativa* de las áreas ocupadas y del inventario de la infraestructura ubicada en zonas de rondas hídricas. La información depende de la actualización de los datos de [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Main_Page), herramienta de construcción colectiva y no está basada en la cartografía oficial.  La infraestructura en esta área puede estar expuesta a inundaciones, movimientos en masa, procesos erosivos, crecientes súbitas y flujos torrenciales.  Los resultados que arroja esta herramienta no sustituyen los estudios y análisis de riesgo para instrumentos de ordenamiento.
    **El [DNP](https://www.dnp.gov.co/DNPN/Paginas/default.aspx) no se hace responsable del uso indebido de la información, la cual debe verse como de  referencia**''',
    style = {
        "font-size": '12px',
        'color': 'gray'
    }),
    ],
    width = 10),
     dbc.Col([
        html.Img(src = './assets/img/warning.ico', width = '50', height = '50')
    ],
    style = {
        'padding':'0'
    },
    width = 1),
],
style = {
    'background-color': '#FBE7AE',
    'padding-top': '6px',
    'padding-bottom': '4px',
    'margin': '0'
},
)



#Se crea una variable para almacenar todos los elementos antes de agregarlos al layout de la app
avant_layout = dbc.Row([
    #columna del panel de datos y el geovisor
    dbc.Col([
        tabs,
        geovisor,
    
    ],

    xl = 7,
    lg = 7,
    md = 7,
    sm = 12,
    xs = 12
    ),

    #columna de resultados
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

#TODO: Hacer que se cargue el archivo primero al servidor y luego cargarlo con la app
#botón de aubir un archivo Shapefile
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



##*************************************HIDDEN DIVS PARA APOYAR LAS FUNCIONALIDADES DE LOS CALLBACKS******************

#TODO: Quitar en caso de que se pueda subir un shapefile
#hidden div para almacenar el objeto geoJSON
hidden_geojson = html.Div(
    id= 'hidden_geojson',
    style={'display':'none',
    'position':'absolute ',
    'top':'990px'}
)

#hidden div para apoyar al callback assign_geodf
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
                
app.layout = html.Div(children = [navbar, disclaimer,
                                  avant_layout,
                                  up_button, 
                                  errorMsj, loading_state, disclaimer,
                                hidden_geojson, hidden_geodf, hiddenvar])





#                     oooo  oooo   .o8                           oooo                 
#                     `888  `888  "888                           `888                 
#  .ooooo.   .oooo.    888   888   888oooo.   .oooo.    .ooooo.   888  oooo   .oooo.o 
# d88' `"Y8 `P  )88b   888   888   d88' `88b `P  )88b  d88' `"Y8  888 .8P'   d88(  "8 
# 888        .oP"888   888   888   888   888  .oP"888  888        888888.    `"Y88b.  
# 888   .o8 d8(  888   888   888   888   888 d8(  888  888   .o8  888 `88b.  o.  )88b 
# `Y8bod8P' `Y888""8o o888o o888o  `Y8bod8P' `Y888""8o `Y8bod8P' o888o o888o 8""888P' 
                                                                                    


"""
           Callback principal, se maneja el botón de buscar y analizar (inputs), se toma información (states) de los elementos del 
            panel de datos y se retornan elementos pertenecientes al panel de resultados o a los mensajes de error (outputs) 

            
            Inputs:
                b_search:       Escucha si el botón buscar es oprimido
                b_analizar:     Escucha si el botón analizar es oprimido
            States:
                searchBar:     Barra búsqueda de lugares
                sel_src:       Selector de fuente de análisis
                e_lat1:        Caja de texto latitud 1
                e_lat2:        Caja de texto latitud 2
                e_lng1:        Caja de texto longitud 1
                e_lng2:        Caja de texto longitud 1
                i_buffer1:     Ancho franja de suceptibilidad afluentes principales
                i_buffer2:     Ancho franja de suceptibilidad afluentes secundarios

            Returns:
                hidden_var:              Var auxiliar usado en callback update_map
                error_msj (displayed):   Flag que determina si se muestra o no el mensaje
                error_msj (message):     Mensaje del error
                loading:                 Determina cuando se muestra el componente de espera
                dash_board:              Determina cuando se ve el panel de resultados
                result1_0:               # de construcciones identificadas
                result1_1:               % del total de construcciones
                result2_0:               # de hectareas identificadas
                graph_1:                 Figura 1
                graph_2:                 Figura 2
                download_div:            Botones de las capas para descargar
                graph_2 (style):         Flag para mostrar o no la figura 2
                
"""

@app.callback(
    [Output(component_id = 'hidden_var',component_property='children'),
     Output(component_id = 'error_msj', component_property='displayed'),
     Output(component_id = 'error_msj',component_property='message'),
     Output(component_id = 'loading', component_property = 'children'),
     Output(component_id = 'dash_board',component_property='style'),
	 Output(component_id = 'result1_0',component_property='children'),
     Output(component_id = 'result1_1',component_property='children'),
     Output(component_id = 'result2_0', component_property='children'),
     Output(component_id = 'graph_1', component_property='figure'),
     Output(component_id = 'graph_2', component_property='figure'),
     Output(component_id = 'download_div', component_property = 'children'),
     Output(component_id = 'graph_2', component_property = "style")],
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
    #Se crea una instancia por default de la clase Download en caso de que no se tenga nada para descargar
    d_object = Download(FILE_PATH)
    default = d_object.download_file()

    #Se crea un estilo por default para graph_2
    d_style_g2 = {
        'width':'385px',
        'height':'320px'
                        }

    if bnt1 is None and bnt2 is None:
        location = (4.5975, -74.0765)
        Map(location= location, zoom= 15).generateMap()
        #############################  RESULT  ####################################
        figure1 = {'data':[go.Pie(visible=False)]}
        figure2 = {'data':[go.Pie(visible=False)]}
        return ['Inicia ', False, ' ', html.Div(' '),{'visibility':'hidden'},
                '', '','', figure1,figure2, default, d_style_g2]
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
                    '', '','', figure1, figure2, default, d_style_g2]
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
                        '', '','', figure1, figure2, default, d_style_g2]
            except:
                #####################################  RESULT  ##################################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['reintentar', True, 'Error de conexión', html.Div(' '),{'visibility':'hidden'},
                        '','','',figure1, figure2, default, d_style_g2]

    else: #El boton analizar es presionado

        try:
            location = ((float(lat1)+float(lat2))*.5, (float(lng1)+float(lng2))*.5)
        except:
            #####################################  RESULT  ######################################
            figure1 = {'data':[go.Pie(visible=False)]}
            figure2 = {'data':[go.Pie(visible=False)]}
            return ['', True, 'Existen campos vacíos o erróneos en los campos de entrada.', html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2, default, d_style_g2]
            
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
                        {'visibility':'hidden'},'','','', figure1, figure2, default, d_style_g2]
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
                            poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
                                                            geometry = 'geometry', crs = poly_rivers.crs)
                        except:
                            poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
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
                        figure1 = {'data': [go.Pie(visible= True, 
                                                   values=[n_builds_sus, n_builds-n_builds_sus],
                                                   labels = ['Dentro de Ronda hídrica', 'Fuera de Ronda hídrica'], 
                                                   hole=0.33, marker_colors = graph_colors,
                                                   insidetextfont={'size':18})],
                                   'layout':go.Layout(margin= go.layout.Margin(l=40, r=40, t=15, b=10,autoexpand = False),
                                                      legend= go.layout.Legend(orientation= 'h', 
                                                                               font={'size':15}))}      
                                   
                        figure2 = {'data': [go.Bar(visible = True, x = ['ÁREA'], y = [total_area_sus], 
                                                    name= 'Área dentro de ronda hídrica', marker_color = graph_colors[0]),
                                             go.Bar(visible = True, x= ['ÁREA'], y = [total_area- total_area_sus], 
                                                    name= 'Área fuera de ronda hídrica', marker_color = graph_colors[1])],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 50,r = 1, t=1, b=50,autoexpand = False),
                                                      legend = go.layout.Legend(orientation= 'h', 
                                                                               font={'size':15}),
                                                      yaxis = go.layout.YAxis(title= 'HECTÁREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))
                                }
                        style = {'width':'770px','visibility':'visible'}
                        

                        return ['builds,rivers,poly', False, ' ', html.Div(' '), style,
                                html.B(str(n_builds_sus) + ' construcciones'), html.B(str(porc_builds)+ ' % del total'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectáreas '),
                                figure1,figure2, download_component , d_style_g2]
                    
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
                                                  labels = ['Dentro de ronda hídrica', 'fuera de ronda hídrica'], marker_colors = graph_colors)],
                                   'layout': go.Layout(margin=go.layout.Margin(l=10, r=95, t=25, b=1,autoexpand = False))}
                        figure2 = {'data': [go.Bar(visible = True, x = ['AREA'], y = [total_area_sus], 
                                                    name= 'Área dentro de ronda hídrica' , marker_color = graph_colors[0]),
                                             go.Bar(visible = True, x= ['AREA'], y = [total_area- total_area_sus], 
                                                    name= 'Área fuera de ronda hídrica', marker_color = graph_colors[1])],
                                   'layout':go.Layout(barmode= 'stack', 
                                                      margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                                      yaxis = go.layout.YAxis(title= 'HECTÁREAS'),
                                                      xaxis = go.layout.XAxis(domain=[0,0.5]))}
                        style = {'width':'770px' ,'visibility':'visible'}
                        return ['builds,rivers', False, ' ', html.Div(' '), style,
                                html.B(str(n_builds_sus) + ' construcciones'), html.B(str(porc_builds)+ ' % del total'), 
                                html.B(str(round(total_area_sus,1))+ ' Hectáreas'),
                                figure1,figure2, download_component, d_style_g2]
                else:
                    Map(location= location, zoom= 15).generateMap()
                    msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default, d_style_g2]
						
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
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
                                                        geometry = 'geometry', crs = poly_rivers.crs)
                    except:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
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
                            '','','',figure1,figure2, download_component, d_style_g2]
                else:
                    roi_param  = rivers.to_crs({'init':'epsg:4326'} )
                    download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param )

                    Map(location= location, zoom= 15).generateMap(rivers=osm._rivers,
                                                                  roi = roi_param,
                                                                  bounding=box_coords)
                    #####################################  RESULT ###################################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    return ['rivers', False, '', html.Div(' '), {'visibility':'hidden'},
                            '','','',figure1,figure2, download_component, d_style_g2]
            else:
                Map(location= location, zoom= 15).generateMap()
                msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default, d_style_g2]
            
        else:
            proj = 'epsg:32618'
            box_google = (float(lat1),float(lng1),float(lat2),float(lng2))
            # objeto de google maps para descarga de imagen satelital 
            gmd = GoogleMapDownloader(coords = box_google, proj=proj)
            ntiles = gmd.computeNtiles()
            #tamano permitido de región de análisis
            if ntiles > 256:
                ###########################  RESULTS  ####################################
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                msj = 'La región de análisis es muy grande, por favor intente con una más pequeña'
                return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                    '','','',figure1,figure2, default, d_style_g2]
            
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
                    img_hsv = cv2.cvtColor(img,cv2.COLOR_RGB2HSV)
                except:
                    # ##########################  RESULTS  ####################################
                    figure1 = {'data':[go.Pie(visible=False)]}
                    figure2 = {'data':[go.Pie(visible=False)]}
                    msj = 'No se puede realizar el análisis por imágenes satelitales, por favor revise las coordenadas'
                    return ['', True, msj, html.Div(' '), {'visibility':'hidden'},
                        '','','',figure1,figure2, default, d_style_g2]
                
                #generando region de analisis en la imagen
                analysis_region = osm.computeROIsuperpixels(buffer1)
                
                # mask image and superpixel computing
                out, m = imtools.maskRasterIm(img, gmd.GT, analysis_region)
                segments = imtools.computeSegments(out, compactness=25, mask = m) 
                
                # ## aqui modelo de clasificacicón de la imagen  ###
                # ##################################################
                Xtest = imtools.Feature_im2hist(img_hsv,segments, nbins=35,clrSpc='hsv')
                Ytest_pred = pipeline.predict(Xtest)
                Ytest_prob = pipeline.predict_proba(Xtest)[:,1]
                Ytest_pred2 = Ytest_prob>0.35
                mask_est = imtools.draw_GT(labels= Ytest_pred2,segments = segments)
                segments[mask_est == 0] = 0
                # ##################################################
                
                #  mapeando los segmentos al mapa de dash  
                seg_polygons = imtools.mapSuperPixels(segments=segments, GT=gmd.GT, verbose=False)
                
                # ####   generando buffer de rios ############
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
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
                                                        geometry = 'geometry', crs = poly_rivers.crs)
                    except:
                        poly_rivers = gpd.GeoDataFrame({'geometry':cascaded_union(poly_rivers.buffer(5).geometry)},
                                                        geometry = 'geometry', 
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
                                                
                    #######################################################################################
                    #Calculando en numero de construcciones que intersectan la zona de susceptibles
                    if roi.shape[0] > 1:
                        builds_sus = np.array([seg_polygons.geometry.intersects(x) for x in roi.geometry])
                        builds_sus = seg_polygons[np.logical_or.reduce(builds_sus)]
                    else:
                        builds_sus = seg_polygons[seg_polygons.geometry.intersects(roi.geometry[0])]
                        
                    if builds_sus.shape[0] == 0:
                        roi_param = roi.to_crs({'init':'epsg:4326'})
                        Map(location= location, zoom= 15).generateMap(rivers=osm._rivers, 
                                                                      roi = roi_param,
                                                                      bounding = box_coords)
                        download_component = d_object.download_file(rivers = osm._rivers, roi = roi.to_crs({'init':'epsg:4326'} ))

                    else:
                        roi_param = roi.to_crs({'init':'epsg:4326'})
                        build_sus_param = builds_sus.to_crs({'init':'epsg:4326'})
                        Map(location= location, zoom= 15).generateMap(superpixels = build_sus_param,
                                                                      rivers=osm._rivers, 
                                                                      roi = roi_param,
                                                                      bounding=box_coords)
                        download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param, builds = build_sus_param)
                        
                    #####################################  RESULT ###################################################
                    # calculo de area
                    try:
                        builds_temp = gpd.GeoDataFrame({'geometry':cascaded_union(builds_sus.geometry)},geometry = 'geometry',
                                                        crs = rivers.crs)
                    except:
                        builds_temp = gpd.GeoDataFrame({'geometry':cascaded_union(builds_sus.geometry)},geometry = 'geometry',
                                                        crs = rivers.crs, index = [0])
                    
                    total_area = np.sum(builds_temp.area)/10000 # hectareas
                    n_builds_sus = np.shape(builds_sus)[0]
                    figure1 = {'data': [go.Bar(visible = True, x = ['ÁREA'], y = [total_area], 
                                        name= 'Área dentro de ronda hídrica', marker_color = graph_colors[0])],
                               'layout':go.Layout(barmode= 'stack', 
                                        margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                        yaxis = go.layout.YAxis(title= 'HECTÁREAS'),
                                        xaxis = go.layout.XAxis(domain=[0,0.5]))
                                }
                    figure2 = {'data':[go.Pie(visible=False)]}
                    
                    
                    style = {'width':'770px','visibility':'visible'}
                    #TODO unir tivers y polyrivers
                    style_figure = {
                        'display': 'none'
                    }
                    download_component = d_object.download_file(rivers = osm._rivers, builds = build_sus_param, roi = roi_param)
                    return ['rivers, poly, superpixels', False, '', html.Div(' '), style,
                            html.B(str(round(total_area,1)) + ' Hectáreas'),html.B(str(n_builds_sus) + ' regiones detectadas'),'',
                            figure1,figure2, download_component, style_figure]
                            
                else:
                    ##################################################################################################
                    roi = rivers.copy()
                    #Calculando en numero de construcciones que intersectan la zona de susceptibles
                    if roi.shape[0] > 1:
                        builds_sus = np.array([seg_polygons.geometry.intersects(x) for x in roi.geometry])
                        builds_sus = seg_polygons[np.logical_or.reduce(builds_sus)]
                    else:
                        builds_sus = seg_polygons[seg_polygons.geometry.intersects(roi.geometry[0])]
                        
                    if builds_sus.shape[0] == 0:
                        roi_param = roi.to_crs({'init':'epsg:4326'})
                        Map(location= location, zoom= 15).generateMap(rivers=osm._rivers, 
                                                                      roi = roi_param,
                                                                      bounding = box_coords)
                        download_component = d_object.download_file(rivers = osm._rivers, roi = roi.to_crs({'init':'epsg:4326'} ))

                    else:
                        roi_param = roi.to_crs({'init':'epsg:4326'})
                        build_sus_param = builds_sus.to_crs({'init':'epsg:4326'})
                        Map(location= location, zoom= 15).generateMap(superpixels = build_sus_param,
                                                                      rivers=osm._rivers, 
                                                                      roi = roi_param,
                                                                      bounding=box_coords)
                        download_component = d_object.download_file(rivers = osm._rivers, roi = roi_param, builds = build_sus_param)
                   
                    # calculo de area
                    try:
                        builds_temp = gpd.GeoDataFrame({'geometry':cascaded_union(builds_sus.geometry)},geometry = 'geometry',
                                                        crs = rivers.crs)
                    except:
                        builds_temp = gpd.GeoDataFrame({'geometry':cascaded_union(builds_sus.geometry)},geometry = 'geometry',
                                                        crs = rivers.crs, index = [0])
                    
                    total_area = np.sum(builds_temp.area)/10000 # hectareas
                    n_builds_sus = np.shape(builds_sus)[0]
                    #####################################  RESULT ###################################################
                    figure1 = {'data': [go.Bar(visible = True, x = ['ÁREA'], y = [total_area], 
                                        name= 'Área dentro de ronda hídrica', marker_color = graph_colors[0])],
                               'layout':go.Layout(barmode= 'stack', 
                                        margin = go.layout.Margin(l= 80,r = 1, t=10, b=25,autoexpand = False),
                                        yaxis = go.layout.YAxis(title= 'HECTÁREAS'),
                                        xaxis = go.layout.XAxis(domain=[0,0.5]))
                                }
                    figure2 = {'data':[go.Pie(visible=False)]}
                    style_figure = {
                        'display': 'none'
                    }

                    style = {'width':'770px','visibility':'visible'}
                    return ['rivers, superpixels', False, '', html.Div(' '), style,
                            html.B(str(round(total_area,1)) + ' Hectáreas'),html.B(str(n_builds_sus) + ' regiones detectadas'),'',
                            figure1,figure2, download_component, style_figure]
            #No hay informacion de capas de rios, por ende no se genera imagen satelital
            else:
                Map(location= location, zoom= 15).generateMap()
                msj = """No hay información disponible de capa de rios
para esta región. Intente de nuevo o cambie
la región de análisis"""
                figure1 = {'data':[go.Pie(visible=False)]}
                figure2 = {'data':[go.Pie(visible=False)]}
                return ['builds', True, msj, html.Div(' '),{'visibility':'hidden'},'','', '',figure1, figure2, default, d_style_g2]   


@app.callback(
        Output(component_id= 'map', component_property = 'srcDoc'),
        [Input(component_id= 'hidden_var',component_property = 'children')]
)
def update_map(value):
    return open('temp1.html','r').read()


"""
           Callback para realizar la funcionalidad de carga
            
            Inputs:
                upload-data:       Contenido que es cargado
            States:
                upload-data:       Nombre del archivo cargado

            Returns:
                hidden_geojson:     Div auxiliar para almacenar el geoJSON
               
"""
#TODO: REGIÓN EN COSTRUCCIÓN

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


"""
           Callback para crear un geodataframe y ponerlo en el mapa
            
            Inputs:
                hidden_geojson:       Contenido que fue cargado
            
            Returns:
                hidden_geodf:         Geodataframe creado a partir del geoJSON
                
"""
#TODO: REGIÓN EN COSTRUCCIÓN
@app.callback(
    Output ('hidden_geodf', 'children'),
    [Input ('hidden_geojson', 'children')]
)
def assign_geodf(geojson):
    if geojson is not None:

        geo_df = gpd.read_file(geojson)
        print("dataframe: {}".format(type(geo_df)))
        print(geo_df['geometry'])


"""
           Callback para generar y descargar el reporte PDF
            
            Inputs:
                report_button:            Botón de generar reporte
                download_report_button:   Botón de descargar reporte
            States:
                e_lat1:                   Valor de latitud 1
                e_lng1:                   Valor de longitud 1
                e_lat2:                   Valor de latitud 2
                e_lng2:                   Valor de longitud 2
                result1_0:                # de construcciones identificadas
                result1_1:                % del total de construcciones
                result2_0:                # de hectareas identificadas
                graph_1:                  Figura 1
                graph_2:                  Figura 2
            Returns:
                download_report_button:   Botón con hipervinculo a archivo PDF
                download_report_button (style):   Estilo que determina si el botón aparece o desaparece  
                report_button:            Estilo que determina si el botón aparece o desaparece
               
"""
@app.callback(
    [Output('download_report_button', 'children'),
    Output('download_report_button', 'style'),
    Output('report_button', 'style')],
    [Input ('report_button', 'n_clicks'),
    Input('download_report_button', 'n_clicks')],
    [State('e_lat1', 'value'),
    State('e_lng1', 'value'),
    State('e_lat2', 'value'),
    State('e_lng2', 'value'),
    State('result1_0', 'children'),
    State('result1_1', 'children'),
    State('result2_0', 'children'),
    State('graph_1', 'figure'),
    State('graph_2', 'figure'),
    ]
)
def generateReport(clicks_generate, clicks_download, lat_1, long_1, lat_2, long_2, result_1, result_2, result_3, graph_1, graph_2):
    
    #Se crean los estilos que se van usar en cada uno de los casos
    dissapear = {
        'display': 'none',
        'color': 'white'
    }

    style_2 = {
        'display': 'flex',  
        'color': 'white',
        'background': '#011f4b'
    }

    style_3 = {
        'display': 'flex',  
        'color': 'white',
        'background': 'red'
    }

    image_analysis_flag = False

     

    if result_3 == "":
        image_analysis_flag = True
        
# se mira cual botón fue presionado
    ctx = dash.callback_context
    if not ctx.triggered:
        
        return ["", dissapear, style_2]
    else:
        which_one = ctx.triggered[0]['prop_id'].split('.')[0]

    if which_one == 'report_button':
        
        if not image_analysis_flag:
            report = Report(lat_1, long_1, lat_2, long_2, result_1['props']['children'], result_2['props']['children'], graph_1, result_3 = result_3['props']['children'], graph_2 = graph_2).generateTemplate()
        else:
            report = Report(lat_1 = lat_1, long_1 = long_1, lat_2 = lat_2, long_2 = long_2, result_1 = result_1['props']['children'], result_2 = result_2['props']['children'], graph_1 = graph_1).generateTemplate()
        
        location = "/report/{}_reporte.pdf".format(report)

        
        download_button =  html.A("Descargar reporte", href = location, style = { "text-decoration" : "none", "color": "white",}) 
       
        
        return [download_button, style_3, dissapear]

    if which_one == 'download_report_button':
        #se vuelve al estado original
        return["", dissapear, style_2]
    
    
    return ["", dissapear, style_2]
    

""" 
        
            Callback para mostrar el componente de carga de PDF
            
            Inputs:
                report_button:           Escucha si el botón generar reporte es oprimido
                download_report_button:  Escucha si el botón descargar reporte es oprimido
            Returns:
                pdf_text:                Texto de espera mientras se genera pdf   
                pdf_spinner:             spinner
"""
@app.callback(
    [Output('pdf_text', 'style'),
    Output('pdf_spinner', 'style')],
    [Input('report_button', 'n_clicks'),
    Input('download_report_button', 'n_clicks'),],
    
)
def display_loading_pdf(clicks, download_clicks):
    dissapear = {
        'display': 'none'
    }

    style_2 = {
             'display':'flex',
             'margin-bottom': '20px'
        }
    ctx = dash.callback_context
    if not ctx.triggered:
        print("entered in not_triggered")
        return [dissapear, dissapear]
    else:
        which_one = ctx.triggered[0]['prop_id'].split('.')[0]
    if which_one == 'report_button':
        return [style_2, style_2]

    if which_one == 'download_report_button':
        return [dissapear, dissapear]
    return  [dissapear, dissapear]


# ****************************** MAIN *****************************
if __name__ == '__main__':
    app.run_server(debug=True)