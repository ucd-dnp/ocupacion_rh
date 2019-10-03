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
- Pyproj
- PDFkit

La especificación de las versiones de las librerías, así como la manera de como estas deben ser instaladas se verá en la sección de [instalación](#instalación) 



## Características

La aplicación consta de un tablero de datos que permite al usuario, con ayuda de mapas de servicios como Open Street Map o también con información obtenida mediante herramientas como Leaflet, delimitar una zona de interés y analizar de allí, las construcciones que se encuentran cerca a los cauces de los ríos.

![general-view](assets\img\general-view.PNG) 

Este análisis se puede llevar a cabo de dos maneras:

- Usando la API de Open Street Map, que permite extraer información correspondiente a los ríos y construcciones que se encuentran en la zona. De igual manera permite crear regiones para llevar a cabo el cálculo de determinar si una construcción se encuentra dentro de un área o no.
- Calculando las construcciones que se encuentran en la zona usando la técnica SLIC y la segmentación de la imagen en _superpixels_ de modo que, si no se tiene información acerca de las construcciones, se pueda identificar mediante este algoritmo, qué construcciones se encuentran en una condición de vulnerabilidad.

## Instalación

Para la instalación de la aplicación, es necesario que externamente se instalen los siguientes programas:

- [plotly Orca](https://github.com/plotly/orca): Se recomienda el método de instalación número 4
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html): Versión _`5.4.2`_ (_Bleeding Edge_)

Se recomienda altamente usar un entorno virtual de Python para ejecutar la aplicación. Esto con el fin de evitar conflictos con otras librerías que puedan estar instaladas. Para esto se sugiere usar la librería [_virtualenv_](https://pypi.org/project/virtualenv/) , disponible en en gestor de paquetes de Python.



#### Windows

Para crear un entorno virtual ejecute el siguiente comando:

```bash
python -m venv <nombre del entorno>
```

Para activar el entorno virtual ejecute:

```bash
cd <nombre del entorno>/Scripts
activate
```

Para la instalación en Windows es necesario que se instalen algunas librerías manualmente, ya que pueden surgir errores si dichas librerías son instaladas desde el gestor de paquetes de Python (_pip_). Para ello, se recomienda buscar estos archivos (archivos _.whl_) en el repositorio del profesor [Cristoph Gohlke](https://www.lfd.uci.edu/~gohlke/pythonlibs/).

Las librerías son las siguientes:

- [Cartopy‑0.17.0‑cp37‑cp37m‑win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#cartopy)
- [Fiona-1.8.6-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona)
- [numpy-1.16.4+mkl-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
- [geopandas-0.5.1-py2.py3-none-any](https://www.lfd.uci.edu/~gohlke/pythonlibs/#geopandas)
- [pyproj-2.1.3-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyproj)
- [Rtree-0.8.3-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#rtree)
- [Shapely-1.6.4.post2-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely)
- [GDAL-2.4.1-cp37-cp37m-win_amd64](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal)

La librería _rasterio_ también es necesaria. Sin embargo, la versión requerida ya no se encuentra en la página antes mencionada, por lo que se decidió incluir este archivo en el repositorio; esta se encuentra en la carpeta _libs_.

Para instalar estas librerías siga estos pasos:

- Normalmente, la forma para instalar archivos _.whl_ es la siguiente:

    ```bash
    pip install <nombre del archivo.whl>	
    ```

    Sin embargo, para automatizar este proceso se creó un script, que instala estas librerías.

- Ubíquese en la carpeta _libs_, descargue todas las librerías mencionadas anteriormente, y ejecute el archivo _config.cmd_ ubicado en la carpeta _libs/windows_ _**Es importante que las librerías que se descarguen, conserven el nombre con el que fueron descargados, de lo contrario este método no funcionará**_. Este script también creará automáticamente archivos y carpetas necesarias para el funcionamiento de la aplicación. 



Para la ejecución de los programas _Orca_ y _wkhtmltopdf_ es necesario que las rutas a estos sean añadidas al _path_ del sistema, para esto se sugiere ver la siguiente [guia](https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/#targetText=To add a new path,click on the Edit button.).

Finalmente ingrese al archivo _env_variables.dat_ e ingrese el _path_ absoluto de las siguientes carpetas:

- _generated_pdf_
- _resources/shp_geojson_

#### Ubuntu y sistemas basados en Debian

Para crear un entorno virtual instale virtualenv:

```bash
sudo apt-get install virtualenv
```

Luego cree un entorno virtual usando:

```bash
virtualenv -p python3.7 <nombre del entorno>
```

Para activar el entorno virtual en Ubuntu o Debian ejecute:

```bash
source <nombre del entorno>/bin/activate
```
Añadimos el siguiente repositorio

```bash
sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
```

Y luego instalamos programas y dependencias que son necesarias para instalar las librerías

```bash
sudo apt-get install libproj-dev proj-data proj-bin libgeos-dev build-essential python3-dev cython3 python3-setuptools python3-pip python3-wheel python3-numpy libz-dev libblosc-dev liblzma-dev liblz4-dev libzstd-dev libpng-dev libwebp-dev libbz2-dev libopenjp2-7-dev libjxr-dev liblcms2-dev libtiff-dev
```

Procedemos entonces a instalar las librerías de python necesarias. Para ello nos ubicamos en la carpeta _libs/linux_ y ejecutamos el archivo config.sh,.

```bash
./config.sh
```

Para la ejecución de los programas _Orca_ y _wkhtmltopdf_ es necesario que las rutas a estos sean añadidas al _path_ del sistema, para esto se sugiere ver la siguiente [guia](https://opensource.com/article/17/6/set-path-linux.).

Finalmente ingrese al archivo _env_variables.dat_ e ingrese el _path_ absoluto de las siguientes carpetas:

- _generated_pdf_
- _resources/shp_geojson_

## Ejecución

Para ejecutar la aplicación, ubíquese en la carpeta donde se encuentra ubicado el programa y ejecute:

```python
python app.py
```




## Testing