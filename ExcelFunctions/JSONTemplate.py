from ExcelFunctions.OpenExcel import get_column_names
import re

def create_template():
    template = ""
    d = {" ": "_", "/": "", "(": "", ")": "", "&": ""}
    for col in get_column_names():
        col = re.sub(r"[\s&]|[\(\)\/]", lambda x: d[x[0]], col)
        template += f'''{col}: null \n'''
    template = f'''{{{template}}}'''
    return template