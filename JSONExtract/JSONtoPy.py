import json
import re

def extract_json(llm_output):
    response = llm_output
    jsondict = json.loads(response)

    list_of_patterns = [r"age", r"marital", r"nationality", r"date_of_birth",
                        r"visit_date", r"visit_time", r"temperature", r"pulse", 
                        r"respiratory", r"bp", r"o2", r"pain_scale", r"gcs", 
                        r"height", r"weight", r"bmi", r"triage", r"chief", 
                        r"past", r"travel", r"medication", r"psychosocial", 
                        r"occupation", r"primary", r"other", r"disease", 
                        r"remarks", r"disposition_type", r"advice", r"condition", 
                        r"disposition_date", r"disposition_time"]
    values = []
    for variable in jsondict.keys():
        for pattern in list_of_patterns:
            if re.search(pattern=pattern, string=variable):
                values.append(jsondict[variable])
    return values
