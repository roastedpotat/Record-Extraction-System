import pandas as pd

def load_in_file(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name, engine= "calamine")
    df = df.drop(columns= ['Unnamed: 36', 'Unnamed: 37', 'Unnamed: 38', 
                           'Unnamed: 39', 'Unnamed: 40', 'Unnamed: 41', 
                           'Unnamed: 42', 'Unnamed: 43', 'Unnamed: 44', 
                           'Unnamed: 45', 'Unnamed: 46', 'Unnamed: 47', 
                           'Unnamed: 48', 'Unnamed: 49', 'Unnamed: 50', 
                           'Unnamed: 51', 'Unnamed: 52', 'Unnamed: 53', 
                           'Unnamed: 54', 'Unnamed: 55', 'Unnamed: 56', 
                           'Unnamed: 57', 'Unnamed: 58', 'Unnamed: 59', 
                           'Unnamed: 60'])
    return df

def get_column_names(df):
    df = df.drop(columns= ['s.no', 'Comp ID', 'Gender', 'Age'])
    columns = df.columns.str.strip().str.lower().to_list()
    return columns

def add_data_to_excel(data, ws, starting_column, row_num, initial_data=None):
    for i, value in enumerate(data):
        for j, initial_value in enumerate(initial_data, start= 1):
            ws.cell(row=int(row_num) + 2, column= j, value=initial_value)
        ws.cell(row=int(row_num) + 2, column=starting_column + i, value=value)

    print(f"Added data to row {row_num + 2}")
    return True