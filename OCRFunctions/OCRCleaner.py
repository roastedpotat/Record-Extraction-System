import re

def clean_ocr(records_dict):
    if not records_dict:
        return
    list_of_patterns = [ r"Primary ICD", r"mobile no[\W] \d{10}", 
                    r"file[\W|\s]no[\W] \d{2}[\W]\d{2}[\W]\d{2}", 
                    r"appt[\W]\s?time:", r"department[\W] accident and emergency", 
                    r"ND EMERGENCY", r"Fall Risk Assesment", 
                    r"Nurse\W?s\s?Note[\W]", r"Vital Reasses?s?ment", 
                    r"Fall Risk Reasses?s?ment", r"Nurse\W?s Note Reassessment", 
                    r"SI.No\s?Nurses Note", r"NCY\(\d*\)?", r"EPORTS"
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
    cleanest = []
    for value in records_dict.values():
        clean = re.sub(pattern= compiled, repl= "", 
                       string= value)
        cleanest.append(clean)
    return cleanest

def master_clean_ocr(records_dict):
    removals = [
        (r"Fall\s*Risk\s*(?:Re)?as+es+ment", "Chief Complaint"), 
        (r"Nurse'?s?\s*Note(?:\s*Reassessment)?", "Past Medical History"),
        (r"Medication\s*Order", "Disposition")
    ]
    cleaned_records = {}
    for key, value in records_dict.items():
        combined_patient_text = ""

        for text in value:
            cleaned_text = text
            for start_pattern, end_anchor in removals:
                pattern = rf"(?i){start_pattern}.*?{re.escape(end_anchor)}"
                cleaned_text = re.sub(pattern, end_anchor, cleaned_text, flags= re.DOTALL)
            combined_patient_text += cleaned_text + "\n\n "
        cleaned_records[key] = re.sub(pattern= r"\n{3,}", repl= "\n\n", string= combined_patient_text)
    total_clean = clean_ocr(cleaned_records)
    return total_clean

def remove_sidebar_noise(records):
    if not records:
        return records
    
    SIDEBAR_NOISE = [
        "Doctor", "All", "ACC", "MEDICAL RECORDS", "LAB REPORTS", "RADIOLOGY REPORTS",
        "OTHER REPORTS", "OTHER DOCUMENTS", "OTHER FILES", 
        "HEMODIALYSIS - NUTRITION", "ASSESSMENT/RE-ASSESSMENT", 
        "VisitRecord", "Departmet", "isil Type", "isit Type",
        "©All OP IP", "©AlI OP IP", ":AL OP OIP", "All OP IP",
    ]
    
    cleaned_records = []
    for record in records:
        lines = record.split('\n')
        cleaned = [line for line in lines if not any(noise in line.strip() for noise in SIDEBAR_NOISE)]
        cleaned_records.append('\n'.join(cleaned))
    return cleaned_records