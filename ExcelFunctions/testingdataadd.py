from openpyxl import load_workbook
import pandas as pd
from JSONExtract.JSONtoPy import extract_json
'''
# General Set up of Opening a Workbook:
filepath = "G:\ER Visits(Above 60) - Jan 2020 to Jun 2025.xlsx"
wb = load_workbook(filename= filepath)
ws = wb["Visit Recs"]

# Adding the data acquired from OCR+LLM process:
for new_data in extract_json():
    ws.append(new_data)

#Saving the work done:
wb.save(filename= filepath)'''
