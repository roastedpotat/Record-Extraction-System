import datetime
import json
import re

def fix_icd_misread(code: str) -> str:
    if isinstance(code, str) and re.match(r'^L[A-Z]\d', code):
        return code[1:]
    return code

def format_time(t):
    if isinstance(t, str):
        t = t.strip().replace(":", "")
        if len(t) == 4 and t.isdigit():
            return f"{t[:2]}:{t[2:]}"
    return t

def age_checker(age, dob, visit):
    if not dob or not visit:
        print("Date is not given properly")
        return
    try:
        birth_date = datetime.strptime(dob, "%d/%m/%Y")
        visit_date = datetime.strptime(visit, "%d/%m/%Y")
        birth_year = birth_date.year
        birth_month = birth_date.month
        birth_day = birth_date.day
        visit_year = visit_date.year
        age_year = visit_year - birth_year
        check_birthday = datetime(visit_year, birth_month, birth_day)
        if check_birthday > visit_date:
            age = age_year - 1
        else:
            age = age_year
        
    except ValueError:
        print(f"Could not parse dates: dob={dob}, visit={visit}")
    return age
        
def extract_json(llm_output):
    jsondict = json.loads(llm_output)

    list_of_patterns = [r"marital", r"nationality", r"date_of_birth",
                        r"visit_date", r"visit_time", r"temperature", r"pulse", 
                        r"respiratory", r"bp", r"o2", r"pain_scale", r"gcs", 
                        r"height", r"weight", r"bmi", r"triage", r"chief", 
                        r"past", r"travel", r"medication", r"psychosocial", 
                        r"occupation", r"primary", r"other", r"disease", 
                        r"remarks", r"disposition_type", r"advice", r"condition", 
                        r"disposition_date", r"disposition_time"]

    for key in jsondict:
        if re.search(r"primary", key):
            jsondict[key] = fix_icd_misread(jsondict[key])
        elif re.search(r"other", key):
            if isinstance(jsondict[key], str):
                codes = jsondict[key].split(",")
                jsondict[key] = [fix_icd_misread(code) for code in codes]
                jsondict[key] = ", ".join(fix_icd_misread(code.strip()) for code in codes)
        if re.search(r"time", key):
            jsondict[key] = format_time(jsondict[key])
        if re.search(r"age", key):
            jsondict[key] = age_checker(age=jsondict[key], 
                                        dob= jsondict.get("date_of_birth"), 
                                        visit= jsondict.get("visit_date"))

    values = []
    for variable in jsondict.keys():
        for pattern in list_of_patterns:
            if re.search(pattern=pattern, string=variable):
                values.append(jsondict[variable])
                break 

    return values