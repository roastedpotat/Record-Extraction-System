import pandas as pd

def load_in_file(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name, engine= "calamine")
    df = df.drop(columns= ["         ", "Unnamed: 36", "Unnamed: 37", 
                       "Unnamed: 38", "Unnamed: 39", "Unnamed: 40", 
                       "Name", "Age", "DATE OF BIRTH"])
    return df

def get_column_names(df):
    columns = df.columns.str.strip().str.lower().to_list()
    return columns