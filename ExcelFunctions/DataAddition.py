# from openpyxl import load_workbook
import pandas as pd

def specific_id_row(dataframe, json_extract):
    for value in json_extract:
        specific_id = value[0]
        rows = dataframe.loc[dataframe['Comp ID']==int(specific_id)]
        return rows

# Make sure main scripts has rows as an object of specific_id_row()

def row_num_checker(rows, total_records):
    flag = False
    total_extract = len(total_records)
    if len(rows)==total_extract:
            flag = True
    return flag

def check_row_data(rows):
    columns = ['Primary ICD', 'Nationality', 'Chief Complaint']
    indices = []
    for i in rows.index:
        row = rows.loc[i]
        for col in columns:
            test = str(row.get(key=col))
            if test != 'nan':
                break
        else:
            indices.append(i)
    return indices
    
def data_per_row():
    pass