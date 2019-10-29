
from datetime import datetime
import plotly
import requests

import jinja2

import pdfkit

import plotly.graph_objects as go


class Report:

    def __init__(self, lat_1, long_1, lat_2, long_2, result_1, result_2, graph_1, result_3 = None, graph_2 = None):
        self.lat_1 = lat_1
        self.long_1 = long_1
        self.lat_2 = lat_2
        self.long_2 = long_2
        self.result_1 = result_1
        self.result_2 = result_2
        self.result_3 = result_3
        self.graph_1 = graph_1
        self.graph_2 = graph_2

    """
           Método para hacer geocoding inverso usando OSM
        
            Returns:
                El nombre del lugar que dió como resultado el reverse geocoding
    """    

    def make_request(self):
        r_url = "https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=10".format(self.lat_1, self.long_1)
        r = requests.get(url = r_url, timeout = 20)
        data = r.json()
        return data['display_name']

    """
           Metodo para generar el template en jinja y convertirlo a PDF
            

            Returns:
                Elnombre del archivo que fue generado
    """
    def generateTemplate(self):
       #fecha que aparecera en los reportes
        report_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        #fecha que aparecera en el nombre de los archivos
        file_name = datetime.now().strftime("%b%d%Y%H%M%S")
        graph_colors = ['rgb(31,119,180)', 'rgb(255,127,14)']

        
        image_analysis_flag = True if self.result_3 is None else False

        #Se convierten las figuras a PNG
        graph_png_1 = go.Figure(self.graph_1)
        graph_png_1.write_image("generated_figures/{}_1.png".format(file_name))

        if not image_analysis_flag:
            graph_png_2 = go.Figure(self.graph_2)
            graph_png_2.write_image("generated_figures/{}_2.png".format(file_name))


        
        localization = self.make_request()

        #Se carga el template
        #codigo de = http://www.marknagelberg.com/creating-pdf-reports-with-python-pdfkit-and-jinja2-templates/
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "report_template.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        
        
        parameters = template.render(date = report_date, localization = localization, result_1 = self.result_1, graph_1 = file_name, graph_2 = file_name,  result_2 = self.result_2, result_3 = self.result_3, lat_1 = self.lat_1, long_1 = self.long_1, lat_2 = self.lat_2, long_2 = self.long_2, flag = image_analysis_flag)
         
        html_file = open("generated_html/{}_html_report.html".format(file_name), 'w')
        html_file.write(parameters)
        html_file.close()

        #Se renderiza el html a pdf
        
        config = pdfkit.configuration(wkhtmltopdf=bytes('C://Program Files//wkhtmltopdf//bin//wkhtmltopdf.exe', 'utf-8'))
        #config = pdfkit.configuration(wkhtmltopdf=bytes('/usr/local/bin/wkhtmltopdf', 'utf-8'))
        pdfkit.from_file("generated_html/{}_html_report.html".format(file_name), "generated_pdf/{}_reporte.pdf".format(file_name), configuration = config)
        return file_name
