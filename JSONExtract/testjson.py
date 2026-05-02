import json
import re
from ExcelFunctions.OpenExcel import get_column_names

def test_json_extract(output):
    for i,value in enumerate(output):
        response = output[i]

        json_file = json.dumps(response)
        load = json.loads(json_file)

        list_of_patterns = [r"comp", r"gender", r"marital", r"nationality", 
                            r"visit.*date", r"visit.*time", 
                            r"temperature", r"pulse", r"respiratory", r"bp", 
                            r"o2", r"pain scale", r"gcs", r"height", r"weight", 
                            r"bmi", r"triage", r"chief", r"past", r"travel", 
                            r"medication", r"psychosocial", r"occupation", 
                            r"primary", r"other", r"disease", r"remarks", 
                            r"disposition.*type", r"advice", r"condition", 
                            r"disposition.*date", r"disposition.*time"]
    # Need to separate out the zip function to run match key and col
        values = []
        for variable,pattern, col in zip(load.keys(),list_of_patterns, get_column_names()):
            if (re.search(pattern=pattern, string=variable, flags= re.IGNORECASE) 
                and re.search(pattern=pattern,string=col, flags= re.IGNORECASE)):
                values.append(load[variable])
        yield values