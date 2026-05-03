import time
start_time = time.perf_counter()
import io
import os
import re
import pandas as pd
from llama_cpp import Llama
from numpy import asarray
from concurrent.futures import ThreadPoolExecutor
from LLMFunctions.LlamaResponse import llm_response
from DriveFunctions.Google import Create_Service
from DriveFunctions.FolderDive import get_ParentFolderId, Search_Folder
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
from paddleocr import PaddleOCR

# Test Updates ================================================================

def DownloadFiles(id):
    test = Create_Service(CLIENT_FILE, API_NAME, API_VER, SCOPES)
    request = test.files().get_media(fileId= id).execute()
    return request

def get_image_file_ids(subfolder_id):
    total_id = []
    for folder_id in subfolder_id:
        file_ids = Search_Folder(body= service, parent_id= folder_id)
        total_id.append(file_ids)
    return total_id

def get_image_bytes(image_file_ids):
    if image_file_ids:
        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(DownloadFiles, image_file_ids))
            print(f"Done")
            return results

def edit_img(img_byte):
    if img_byte:
        imgbyte = io.BytesIO(img_byte)
        img = Image.open(imgbyte)
        ratio = 2000/max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        resized_img = img.resize(new_size)
        blur_img = resized_img.filter(ImageFilter.GaussianBlur(radius=2)) # Old radius = 2
        contrast_img = ImageEnhance.Contrast(blur_img).enhance(2.0) # Old Contrast = 2
        sharp_img = ImageEnhance.Sharpness(contrast_img).enhance(3.0) # Old Sharpness = 1.5 , Best = 2.5
        autocontrast_img = ImageOps.autocontrast(sharp_img, cutoff=4)
        readable_img = asarray(autocontrast_img)
        img.close()
        return readable_img

def Text_from_images(ocr, readable_list):
    results = ocr.predict(readable_list)
    for item in results:
        texts = item.get('rec_texts', [])
        string = " ".join(texts)
        yield string

def Record_Grouping_with_Dates(texts):
    record_groups = dict()
    current_key = None
    query = r"Visit Date[\W|\w]\s?(\d{2})[\W|\w]\s?(\d{2})[\W|\w]\s?(\d{4})"
    for records in texts:
        search = re.search(query, records, re.IGNORECASE)
        if search:
            key = search.groups()
            clean_key = " ".join(key)
            if clean_key not in record_groups.keys():
                record_groups[clean_key] = []
            record_groups[clean_key].append(records)
            current_key = clean_key
        else:
            record_groups[current_key].append(records)
    return record_groups

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

def load_in_file(filepath, sheet_name):
    df = pd.read_excel(filepath, sheet_name, engine= "calamine")
    df = df.drop(columns= ["         ", "Unnamed: 36", "Unnamed: 37", 
                       "Unnamed: 38", "Unnamed: 39", "Unnamed: 40", 
                       "Name", "Age", "DATE OF BIRTH"])
    return df

def get_column_names(df):
    columns = df.columns.str.strip().str.lower().to_list()
    return columns

def create_template(column_names):
    template = ""
    d = {" ": "_", "/": "", "(": "", ")": "", "&": ""}
    for col in column_names:
        col = re.sub(r"[\s&]|[\(\)\/]", lambda x: d[x[0]], col)
        template += f'''{col}: null \n'''
    template = f'''{{{template}}}'''
    return template

# =============================================================================

CLIENT_FILE = 'credentials.json'
API_NAME = 'drive'
API_VER = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

filepath = r"G:\\ER Visits(Above 60) - Jan 2020 to Jun 2025.xlsx"

sheet_name= "Visit Recs"

file = load_in_file(filepath= filepath, sheet_name= sheet_name)

column_names = get_column_names(file)

json_template = create_template(column_names)

system_content = '''You are a strict medical data extractor. Extract only 
                  what is explicitly present in the text. Never invent or 
                  infer data. If a field is not found, use null.'''

prompt = '''### EXTRACTION RULES:
1. **comp_id:** Find "Hospital ID:" and return only the number after it.
2. **gender:** Find "DOB | Age | Gender:" and return only the gender value after the second |.
3. **nationality:** Find "Nationality:" and return only the nationality value.
4. **marital_status:** Find "Marital Status:" and return only the value after it.
5. **primary_icd:** Find the Provisional Diagnosis table, that lists all the ICD entries. From that table, take the ONLY ICD entry that is immediately followed by the word. Return that entry as: [Code] [Description]. Ignore all other entries.
6. **visit_date / visit_time:** Find the FIRST occurrence of "Visit Date:" followed by DD/MM/YYYY then a 4-digit time. Split into separate fields. If the date separator is missing (e.g. "08/08 2020"), reconstruct it as DD/MM/YYYY.
7. **Vitals:** Extract temperature, pulse, respiratory rate, BP, and O2 saturation from the FIRST vitals reading only. O2 saturation is the number immediately before or after the first \\% \\symbol in the vitals section.
8. **disposition_date / disposition_time:** Go to the absolute end of the provided text. Search backwards from the very last character until you hit the first date and time pair. This value is likely the discharge/disposition time. Ignore all earlier timestamps found in the Triage or Vitals sections. Ensure the time you extract is specifically the one associated with the end of the patient's visit.
9. **pain_scale_score:** Find the FIRST occurrence of "Numerical(X)". Return only the integer X. Do not confuse with GCS.
10. **gcs:** Find the GCS value in the vitals section. Format is typically XX/15. Return only the numerator.
11. **triage_category:** Find the FIRST occurrence of "Triage Category:" and return only the number after it.
12. **chief_complaint:** Find the FIRST occurrence of "Chief Complaint & History of Present Illness" or "Chief Complaint and History of Present Illness". Extract only the text that comes after "Triage Category: X" within that heading. Stop before "Past History" or any other section heading.
13. **past_history:** Find the FIRST occurrence of "Past History:" or "Past Medical History". Extract only the text directly after it. Stop before "Travel History:". Do not include the label itself.
14. **travel_history:** Find the FIRST occurrence of "Travel History:". Extract only the text directly after it. If the value is a date, noise, or navigation text, use null.
15. **current_medication:** Find the FIRST occurrence of "Current Medication". Extract only text directly after it. Stop at "Medical Prescription" or "Medication Order".
16. **psychosocial:** Find the FIRST occurrence of "Psychosocial:" and extract only the text after it. Do not include occupation.
17. **occupation:** Find the FIRST occurrence of "Occupation:" and extract only the text directly after it.
18. **other_icd:** Return the remaining codes only (no descriptions) found in Provisional Diagnosis table where ICD is NOT followed by "Yes", comma-separated.
19. **disease_grouping:** Unless specified, leave as null.
20. **remarks:** Only add remarks if it is found after Provisional Diagnosis Table and before Medication Order Table, or else leave it as null.
21. **advice_health_education:** Find the FIRST occurrence of "Advice & Health Education:" and return only the text immediately after it. Stop at "Education Given To:" or any other label.
22. **condition_at_disposition:** Find "Condition at the time of Disposition:" or "Condition at the tine of Disposition:" and return only the value after it.
23. **disposition_type:** Find "Disposition Type:" and return only the value after it.
'''

ocr_engine = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation= True,
    text_recognition_batch_size=10, 
    text_det_limit_side_len= 2000,
    text_det_limit_type= 'max',
    text_det_box_thresh= 0.5,
    text_det_thresh= 0.2,
    lang='en',
    device= 'cpu',
    enable_mkldnn=True,
    cpu_threads=4,
    )

llm_engine = Llama(model_path= r"G:\\models\\qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
                chat_format= "chatml",
                flash_attn= True,
                n_gpu_layers=-1,
                seed= 1337,
                n_ctx= 8192,
                verbose= False)

service = Create_Service(CLIENT_FILE, API_NAME, API_VER, SCOPES)

parent_folder_id = get_ParentFolderId(body= service, 
                                      text= 'Test UploadFolder')

subfolder_ids = Search_Folder(body= service, parent_id= parent_folder_id)

for folder in subfolder_ids:
    image_ids = Search_Folder(body= service, parent_id= folder)

    image_bytes = get_image_bytes(image_file_ids= image_ids)

    readable_img = []
    with ThreadPoolExecutor(max_workers=16) as Executor:
        if image_bytes:
            readable_img = list(Executor.map(edit_img, image_bytes))

    texts = list(Text_from_images(ocr= ocr_engine, readable_list= readable_img))
    print("OCR done!")
    record = Record_Grouping_with_Dates(texts= texts)
    print("Cleaning Started!")
    clean_records = list(clean_ocr(records_dict= record))
    print("LLM processing...")
    llm_step = list(llm_response(llm= llm_engine, clean_records= clean_records, 
                                 column_names= column_names, prompt= prompt, 
                                 system_content= system_content))
    for step in llm_step:
        print(step)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Took a total of {elapsed_time:.1f} seconds")