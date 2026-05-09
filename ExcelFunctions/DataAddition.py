# from openpyxl import load_workbook
import pandas as pd

def specific_id_row(dataframe, specific_id):
    rows = dataframe.loc[dataframe['Comp ID']==int(specific_id)]
    return rows

# Make sure main scripts has rows as an object of specific_id_row()

def row_num_checker(rows, total_records):
    total_extract = len(total_records)
    if len(rows)==total_extract:
            flag = 0
    elif len(rows)>total_extract:
            flag = 0
    else:
        flag = total_extract - len(rows)
    return flag

def check_row_data(rows):
    columns = ['Primary ICD', 'Nationality', 'Chief Complaint']
    indices = []
    for i in rows.index:
        row = rows.loc[i]
        if any(str(row.get(key=col)) == 'nan' for col in columns):
            indices.append(int(i))
    return indices
    
def data_per_row(df, records, comp_id):
    dates = df.loc[df['Comp ID'] == int(comp_id), 'Visit Date']
    proper_dates = pd.to_datetime(dates, 
                                  errors='coerce', 
                                  dayfirst= True).dt.strftime("%d-%m-%Y").tolist()
    data = dict()
    errors = []
    for key,value in records.items():
        proper_key = pd.to_datetime(key, 
                                    errors='coerce', 
                                    dayfirst= True).strftime("%d-%m-%Y")
        if not proper_key in proper_dates:
            data[key] = value
        elif pd.isna(proper_key):
            errors.append((f"Comp ID: {comp_id} | Date key: {key}\n"))
            data[key] = value
    if errors:
        print(f'''Errors found for Comp ID {comp_id}. 
              Check data_errors.txt for details.''')
        with open("data_errors.txt", "a") as f:
            f.writelines(errors)
    return data