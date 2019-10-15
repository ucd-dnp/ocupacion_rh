FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN apt-add-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt-get install -y \
libproj-dev \
proj-data \
proj-bin \
libgeos-dev \
build-essential \
python3-dev \
cython3 \
python3-setuptools \
python3-pip \
python3-wheel \
python3-numpy \
libz-dev \
libblosc-dev \
liblzma-dev \
liblz4-dev \
libzstd-dev \
libpng-dev \
libwebp-dev \
libbz2-dev \
libopenjp2-7-dev \
libjxr-dev \
liblcms2-dev \
libtiff-dev \
libgdal-dev \
gdal-bin \
python-gdal \
libspatialindex-dev \
        inkscape \
        jed \
        libsm6 \
        libxext-dev \
        libxrender1 \
        lmodern \
        netcat \
        unzip \
        nano \
        curl \
        wget \
        gfortran \
        cmake \
        bsdtar  \
        rsync \
        imagemagick \
        gnuplot-x11 \
        libxtst6 \
        libgtk2.0.0 \
        libgconf2-4 \
        xvfb \
        libxss1 \
        libopenblas-base \
        python3-dev \
        xauth \
        libasound2 \
	xfonts-75dpi \
	xfonts-base      



COPY requirements.txt /tmp/
COPY ./app /app

#Installing Wkhtmltopdf
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_1.5.2-0ubuntu5_amd64.deb
RUN dpkg -i libjpeg-turbo8_1.5.2-0ubuntu5_amd64.deb

RUN wget http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb
RUN dpkg -i libpng12-0_1.2.54-1ubuntu1.1_amd64.deb


RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.0/libssl1.0.0_1.0.2n-1ubuntu5.3_amd64.deb
RUN dpkg -i libssl1.0.0_1.0.2n-1ubuntu5.3_amd64.deb

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu52_52.1-3ubuntu0.8_amd64.deb
RUN dpkg -i libicu52_52.1-3ubuntu0.8_amd64.deb

#RUN wget https://bitbucket.org/wkhtmltopdf/wkhtmltopdf/downloads/wkhtmltox-0.13.0-alpha-7b36694_linux-trusty-amd64.deb
#RUN dpkg -i wkhtmltox-0.13.0-alpha-7b36694_linux-trusty-amd64.deb
#RUN cd /usr/local/bin && cp wkhtmltopdf /usr/bin/wkhtmltopdf

RUN apt-get install wkhtmltopdf -y
RUN apt-get install xvfb -y
RUN printf '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf -q $*' > /usr/bin/wkhtmltopdf.sh
RUN chmod a+x /usr/bin/wkhtmltopdf.sh
RUN ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf
  
RUN pip install headless-pdfkit


# Download orca AppImage, extract it, and make it executable under xvfb
RUN wget https://github.com/plotly/orca/releases/download/v1.1.1/orca-1.1.1-x86_64.AppImage -P /home
RUN chmod 777 /home/orca-1.1.1-x86_64.AppImage

# To avoid the need for FUSE, extract the AppImage into a directory (name squashfs-root by default)
RUN cd /home && /home/orca-1.1.1-x86_64.AppImage --appimage-extract
RUN printf '#!/bin/bash \nxvfb-run --auto-servernum --server-args "-screen 0 640x480x24" /home/squashfs-root/app/orca "$@"' > /usr/bin/orca
RUN chmod 777 /usr/bin/orca
RUN chmod -R 777 /home/squashfs-root/

RUN pip download GDAL==2.1.0
RUN tar -xvzf GDAL-2.1.0.tar.gz
RUN cd GDAL-2.1.0 && python setup.py build_ext --include-dirs=/usr/include/gdal/ && python setup.py install

#RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
#RUN export C_INCLUDE_PATH=/usr/include/gdal
#RUN pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==2.4.0
#RUN pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}') --global-option=build_ext --global-option="-I/usr/include/gdal"
RUN pip install -U pip && pip install -r /tmp/requirements.txt --no-cache-dir

RUN touch /etc/nginx/conf.d/custom_timeout.conf && echo "uwsgi_read_timeout 1000s;fastcgi_read_timeout 600;proxy_read_timeout 600;" > /etc/nginx/conf.d/custom_timeout.conf


ENV NGINX_WORKER_PROCESSES auto


