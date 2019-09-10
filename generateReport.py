#library for getting the current datetime for printing in the report
from datetime import datetime
import plotly
import requests
#library for creating the template
import jinja2
#lib for create pdf
import pdfkit
# from weasyprint import HTML, CSS


class Report:

    def __init__(self, lat, long, result_1, result_2, result_3, graph_1, graph_2):
        self.lat = lat
        self.long = long
        self.result_1 = result_1
        self.result_2 = result_2
        self.result_3 = result_3
        self.graph_1 = graph_1
        self.graph_2 = graph_2
    
    #method for make the reverse geocoding request and return the place
    def make_request(self):
        r_url = "https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}&zoom=10".format(self.lat, self.long)
        r = requests.get(url = r_url)
        data = r.json()
        return data['display_name']

    def generateTemplate(self):
       #create the date (formatted) that will appear on the report
        report_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        #create the date that will be on the html file form avoid concurrent conflicts
        graph_date = datetime.now().strftime("%b%d%Y%H%M%S")
        #download the report plot
        plotly.offline.plot(self.graph_1, filename = "generated_figures/{}_1.html".format(graph_date), auto_open = False)
        plotly.offline.plot(self.graph_2, filename = "generated_figures/{}_2.html".format(graph_date), auto_open = False)
        #reverse geocoding
        localization = self.make_request()

        #loading the template
        #code from = http://www.marknagelberg.com/creating-pdf-reports-with-python-pdfkit-and-jinja2-templates/
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "report_template.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        parameters = template.render(date = report_date, localization = localization, graph_1 = graph_date, graph_2 = graph_date)
        html_file = open("{}_html_report.html".format(graph_date), 'w')
        html_file.write(parameters)
        html_file.close()

        #converting and writing into pdf
        
        css_file = "bootstrap.css"
        config = pdfkit.configuration(wkhtmltopdf=bytes('C://Program Files//wkhtmltopdf//bin//wkhtmltopdf.exe', 'utf-8'))
        pdfkit.from_file("{}_html_report.html".format(graph_date), "generated_pdf\{}_reporte.pdf".format(graph_date), configuration = config)
       
