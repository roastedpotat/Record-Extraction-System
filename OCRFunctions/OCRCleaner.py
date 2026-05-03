import re

def clean_ocr(records_dict):
    
    list_of_patterns = [r"mobile no[\W] \d{10}", 
                    r"file[\W|\s]no[\W] \d{2}[\W]\d{2}[\W]\d{2}", 
                    r"appt[\W]\s?time:", r"department[\W] accident and emergency", 
                    r"ND EMERGENCY", r"Fall Risk Assesment", 
                    r"Nurse\W?s\s?Note[\W]", r"Vital Reasses?s?ment", 
                    r"Fall Risk Reasses?s?ment", r"Nurse\W?s Note Reassessment", 
                    r"SI.No\s?Nurses Note", 
                    r"\S*[\W]thumbay[\W]int\S*", r"PVR\s?ID[\W] \d{6}", 
                    r"I?DENT AND EMERGE", r"\S*\(\d*-(\s?\d*\)?)", 
                    r"Thumbay University", r"EMERGEN",
                    r"Generic\s?Name\s?Brand\s?\s?All\s?Instructions\s?Route", 
                    r"\s?Administrated\s?on\s?(No\s?)?Administrated\s?By", 
                    r"\s?Service\s?id[\W]\s?", r"CPTCODE[\W]\s?\d*[\W]",
                    r"(\w*)?\W?(\w*)?\W?(\w*)?(\W*)?(\w*)?(\W*)?(\w*)?/W(\d*)?\W(\w*)?\W(\w*)?", 
                    r"\w*[\W]studentpharma\s"] #r"[\W]\d*[\W]\d*[\W]\s\d*",
    
    patterns = "|".join(list_of_patterns)
    
    compiled = re.compile(pattern= patterns, flags= re.IGNORECASE)


    for value in records_dict.values():
        cleanest = []
        for x in value:
            clean = re.sub(pattern= compiled, repl= "", 
                           string= x)
            cleanest.append(clean)
        yield cleanest
