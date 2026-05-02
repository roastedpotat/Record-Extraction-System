import json
import re
from ExcelFunctions.OpenExcel import get_column_names
from LLMFunctions.LLMResponse import llm_response

def extract_json(llm_output):
    response = llm_output
    jsondict = json.loads(response)

    list_of_patterns = [r"comp", r"gender", r"marital", r"nationality", 
                        r"visit date", r"visit time", r"temperature", r"pulse", 
                        r"respiratory", r"bp", r"o2", r"pain scale", r"gcs", 
                        r"height", r"weight", r"bmi", r"triage", r"chief", 
                        r"past", r"travel", r"medication", r"psychosocial", 
                        r"occupation", r"primary", r"other", r"disease", 
                        r"remarks", r"disposition time", r"advice", r"condition", 
                        r"disposition date", r"disposition time"]
    values = []
    for variable,pattern, col in zip(jsondict.keys(),list_of_patterns, get_column_names()):
        if re.search(pattern=pattern, string=variable) and re.search(pattern=pattern,string=col):
            values.append(jsondict[variable])
    yield values
