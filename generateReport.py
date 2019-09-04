#library for getting the current datetime for printing in the report
from datetime import datetime


class Report:

    def __init__(self, lat, long, result_1, result_2, result_3, map_c):
        lat = self.lat
        long = self.long
        result_1 = self.result_1
        result_2 = self.result_2
        result_3 = self.result_3
        map_c = self.map_c

    def generateTemplate():
        title = '<h1 style = "margin:auto"> Reporte de resultados </h1>'
        date = datetime.now().strftime("%d-%m-%Y H%:%M:%S")
        date_html = '<p> Generado el    '