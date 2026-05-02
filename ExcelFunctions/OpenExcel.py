import pandas as pd

def load_in_file():
    filepath = "G:\ER Visits(Above 60) - Jan 2020 to Jun 2025.xlsx"
    df = pd.read_excel(filepath, sheet_name= "Visit Recs", engine= "calamine")
    df = df.drop(columns= ["         ", "Unnamed: 36", "Unnamed: 37", 
                       "Unnamed: 38", "Unnamed: 39", "Unnamed: 40", 
                       "Name", "Age", "DATE OF BIRTH"])
    return df

def get_column_names():
    df = load_in_file()
    columns = df.columns.str.strip().str.lower().to_list()
    return columns