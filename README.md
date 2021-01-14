![DNPLOGO](app/assets/img/dnp.PNG)

# Herramienta para identificar áreas ocupadas y conteo de infraestructura en zonas de ronda hídrica (RH).

Esta es una aplicación destinada a detectar construcciones que se encuentran en condición de susceptibilidad de ser inundadas, dada su posición con respecto a los cauces de  los ríos.  

La aplicación brinda la posibilidad de analizar distintas regiones de Colombia, incluso cuando los servicios de georreferenciación no tengan datos completos de construcciones en las zonas de interés.

## Contenido

1. [Tecnologías usadas](#tecnologías)
2. [Características](#características)
3. [Instalación](#instalación)
4. [Ejecución](#ejecución)
5. [Piloto DataSandbox](#piloto)

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
- Reverse Geocoder

La especificación de las versiones de las librerías, así como la manera de como estas deben ser instaladas se verá en la sección de [instalación](#instalación) 



## Características

La aplicación consta de un tablero de datos que permite al usuario, con ayuda de mapas de servicios como Open Street Map o también con información obtenida mediante herramientas como Leaflet, delimitar una zona de interés y analizar de allí, las construcciones que se encuentran cerca a los cauces de los ríos.

![GeneralView](app/assets/img/screen.PNG)

Este análisis se puede llevar a cabo de dos maneras:

- Usando la API de Open Street Map, que permite extraer información correspondiente a los ríos y construcciones que se encuentran en la zona. De igual manera permite crear regiones para llevar a cabo el cálculo de determinar si una construcción se encuentra dentro de un área o no.
- Calculando las construcciones que se encuentran en la zona usando la técnica SLIC y la segmentación de la imagen en _superpixels_ de modo que, si no se tiene información acerca de las construcciones, se pueda identificar mediante este algoritmo, qué construcciones se encuentran en una condición de vulnerabilidad.

## Instalación

Para la instalación de la aplicación, es necesario que externamente se instalen los siguientes programas:

- [plotly Orca](https://github.com/plotly/orca): Se recomienda el método de instalación número 4
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html): Versión _`5.4.2`_ (_Bleeding Edge_)

Se recomienda altamente usar un entorno virtual de Python para ejecutar la aplicación. Esto con el fin de evitar conflictos con otras librerías que puedan estar instaladas. Para esto se sugiere usar la librería [_virtualenv_](https://pypi.org/project/virtualenv/) , disponible en en gestor de paquetes de Python.

#### Docker

La manera recomendad y más sencilla para instalar la aplicación es mediante un contenedor de [_Docker_](https://docs.docker.com/). Para esto, luego de seguir la [instalación](https://docs.docker.com/install/) se tienen que seguir los siguientes pasos:

1. Ubíquese en la carpeta raíz del proyecto, en esta se ubica un archivo llamado _Dockerfile_ 

2. Ejecute el siguiente comando:

   ```bash
   docker build -t <nombre de la imagen> .
   ```

   Esto configurará e instalará todas las dependencias y programas necesarios para la correcta ejecución de la aplicación.

3. Para crear un contenedor que corra la imagen anteriormente creada ejecute el siguiente comando:

   ```bash
   docker run -d --name <nombre del contenedor> -p 80:80 <nombre de la imagen>
   ```

   Esto ejecutará el contenedor, lo que significa que la aplicación esta en ejecución.

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

Procedemos entonces a instalar las librerías de python necesarias. Para ello nos ubicamos en la carpeta _libs/linux_ y ejecutamos el archivo config.sh.

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
python app/main.py
```

Ingrese a la siguiente dirección web: _localhost:80_ desde un navegador web (**Se recomienda NO usar la aplicación desde los navegadores Mozilla Firefox e Internet Explorer**)

## Piloto DataSandbox Colombia

El DataSandbox Colombia es un espacio experimental que busca promover el uso de Big Data en el sector público a nivel nacional. Esta sección presenta un proyecto piloto en el cual se desarrolló un modelo automático de detección de construcciones a partir de imágenes satelitales. El objetivo de este trabajo es explorar posibles mejoras al modelo de clasificación de imágenes actual haciendo uso de metodologías compatibles con el DataSandbox. Además, se busca integrar el uso de información georreferenciada del portal de datos abiertos catastral del  Instituto Geográfico Agustín Codazzi [(IGAC)]( https://geoportal.igac.gov.co/contenido/datos-abiertos-catastro). 

El piloto se desarrolló en 4 etapas principales; ingesta de datos, procesamiento, modelado y obtención de resultados. 

* La **ingesta de datos** consistió en obtener un conjunto de imágenes satelital (RGB), sin nubosidad, con buena iluminación y  disponibilidad de datos catastrales actualizados. Esta información se obtuvo de GoogleMaps y del portal de datos abiertos del IGAC. 

* Los datos obtenidos fueron **procesados** para realizar la búsqueda y entrenamiento del modelo de predicción. En primer lugar, el procesamiento consiste en aplicar la ecualización de histogramas de color (RGB) a las imágenes. Posteriormente se transforman al formato HSV y se dividen en cuadrillas de 8x8 pixeles, lo que equivale a 69.65 metros cuadrados aproximadamente.  Para cada cuadrante se extrajo 35 atributos por canal y se asignó una etiqueta según la presencia de construcciones en su interior. 

  En suma, se procesaron 4 imágenes Satelitales para la etapa de modelado. De estas imágenes se obtuvieron 65072 cuadrillas, cada una de ellas con 35 características por canal (HSV), y una etiqueta que indica si el área contiene o no infraestructuras construidas.  

* En la etapa de **modelado** se abordó un problema de clasificación supervisado en el que se buscaba predecir si cada cuadrilla de 8x8 pixeles era o no un área con construcciones.  Para ello se evaluaron múltiples algoritmos con diferentes configuraciones de parámetros. Entre estos, los modelos que arrojaron mayor valor-F1 fueron un *XGboost* y un *Support Vector Classifier* (SVC). Sin embargo, el modelo *XGboost* emplea un tiempo de computación menor al empleado por el SVC. Esto, sumado a mejores resultados de desempeño,  hizo que se escogiera el modelo *XGboost* para realizar la predicción de áreas con infraestructura construida. Las métricas de rendimiento de dichos modelos se presentan a continuación:

  | Modelo    | Precisión | Sensibilidad | Exactitud | Puntaje F1 |
  | --------- | --------- | ------------ | --------- | ---------- |
  | *XGboost* | 0.830     | 0.907        | 0.862     | 0.867      |
  | SVC       | 0.816     | 0.913        | 0.855     | 0.862      |

  Estos resultados fueron obtenidos sobre 9761 observaciones que corresponden a cuadrillas de 8x8 pixeles seleccionadas aleatoriamente para evaluar el desempeño de los modelos.

* Por último, el modelo de predicción *XGboost* es integrado a un proceso de **generación de resultados** en el que, a partir de coordenadas que encierran la región de análisis se obtienen datos estimados de áreas con infraestructura construida.  

Para mayor información, consultar el reporte explicativo de la [metodologia](https://github.com/ucd-dnp/inudaciones_ucd/blob/master/app/Prueba.py).

### Resultados estimados con el modelo 

Aplicando la metodología descrita se obtuvieron los siguientes resultados. Estos pueden ser consultados en el portal de [Datos Abiertos Colombia](https://www.datos.gov.co). 

| Nombre del Archivo  | Municipio | Número de registros | Enlace                                                       |
| ------------------- | --------- | ------------------- | ------------------------------------------------------------ |
| DNP-XGboostPitalito | Pitalito  | 8732                | [DNP-XGboostPitalito \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostPitalito/rntx-zf96) |
| DNP-XGboostPiendamo | Piendamó  | 4058                | [DNP-XGboostPiendamo \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostPiendamo/wpdi-vtc6) |
| DNP-XGboostLaPlata  | La Plata  | 16642               | [DNP-XGboostLaPlata \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostLaPlata/8w42-7pfy) |
| DNP-XGboostGarzon   | Garzón    | 10348               | [DNP-XGboostGarzon \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostGarzon/6vk6-j6ze) |
| DNP-XGboostCerete   | Cereté    | 11233               | [DNP-XGboostCerete \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostCerete/dbfh-gi8w) |
| DNP-XGboostCartago  | Cartago   | 13882               | [DNP-XGboostCartago \| Datos Abiertos Colombia](https://www.datos.gov.co/Mapas-Nacionales/DNP-XGboostCartago/jewm-5u37) |

Los datos fueron generados el 28 de diciembre del 2020 y cuentan con un formato de proyección MagnaSirgas(EPSG:3115). Estos pueden ser descargados en diferentes formatos (como Shapefile o GeoJson), que  permiten utilizarlos en programas de análisis GIS como ArcMap o QGIS. 

