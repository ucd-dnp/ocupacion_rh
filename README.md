![DNPLOGO](assets/img/dnp.PNG)

# Aplicación para detectar zonas susceptibles de inundación debido a su cercanía con las rondas de los ríos.

Esta es una aplicación destinada a detectar construcciones que se encuentran en condición de susceptibilidad de ser inundadas, dada su posición con respecto a los cauces de  los ríos.  

La aplicación brinda la posibilidad de analizar distintas regiones de Colombia, incluso cuando los servicios de georeferenciación no tengan datos completos de construcciones en las zonas de interés.

## Tecnologías usadas

Esta herramienta fue construida usando el Framework de Python llamado [Plotly Dash](https://github.com/plotly/dash). Para la construcción de la aplicación se usó la versión _3.7.4_ de Python

De igual manera se usaron las siguientes librerías:

- OpenCV
- GDAL
- Fiona
- Shapely
- Geopandas
- Rasterio
- Tifffile
- Request
- GeoJSON
- Folium
- Sklearn
- Scikit-image
- OpenCV
- Descartes
- Nominatim
- Plotly
- Geopy
- Numpy
- Pandas
- Matplotlib
- Dash-daq

La especificación de las versiones de las librerías, así como la manera de como estas deben ser instaladas se verá en la sección de [instalación](#instalación) 



## Características

La aplicación consta de un tablero de datos que permite al usuario, con ayuda de mapas de servicios como Open Street Map o también con información obtenida mediante herramientas como Leaflet, delimitar una zona de interés y analizar de allí, las construcciones que se encuentran cerca a los cauces de los ríos.

![general-view](assets\img\general-view.PNG) 

Este análisis se puede llevar a cabo de dos maneras:

- Usando el API de Open Street Map, que permite extraer información correspondiente a los ríos y construcciones que se encuentran en la zona. De igual manera permite crear regiones para llevar a cabo el cálculo de determinar si una construcción se encuentra dentro de un área o no.
- Calculando las construcciones que se encuentran en la zona usando la técnica SLIC y la segmentación de la imagen en _superpixels_ de modo que, si no se tiene información acerca de las construcciones, se pueda identificar mediante este algoritmo, qué construcciones se encuentran en una condición de vulnerabilidad.

## Instalación

Para la instalación de la aplicación, es necesario que externamente se instalen los siguientes programas:

- [plotly Orca](https://github.com/plotly/orca): Se recomienda el método de instalación número 4
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html): Versión _`5.4.2`_ (_Bleeding Edge_)

Se recomienda altamente usar un entorno virtual de Python para ejecutar la aplicación. Esto con el fin de evitar conflictos con otras librerías que puedan estar instaladas. Para esto se sugiere usar la librería [_virtualenv_](https://pypi.org/project/virtualenv/) , disponible en en gestor de paquetes de Python.

Para crear un entorno virtual ejecute el siguiente comando:

```bash
python -m venv <nombre del entorno>
```

#### Windows

Para activar el entorno virtual en Windows ejecute:

```bash
cd <nombre del entorno>/Scripts
activate
```

Para la instalación en Windows es necesario que se instalen algunas librerías manualmente, ya que pueden surgir errores si dichas librerías son instaladas desde el gestor de paquetes de Python (_pip_). Para ello, se recomienda buscar estos archivos (archivos _.whl_) en el repositorio del profesor [Cristoph Gohlke](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

Para instalar estas librerías se proponen dos formas:

- 



#### Ubuntu y sistemas basados en Debian

Para activar el entorno virtual en Ubuntu o Debian ejecute:

```bash
<nombre del entorno>/bin/activate
```



## Ejecución

Para ejecutar la aplicación, ubíquese en la carpeta del programa y ejecute:

```python
python app.py
```



## Testing