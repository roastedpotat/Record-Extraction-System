import time
start_time = time.perf_counter()
import os
from llama_cpp import Llama
from concurrent.futures import ThreadPoolExecutor
from LLMFunctions.LlamaResponse import llm_response
from DriveFunctions.Google import Create_Service
from DriveFunctions.FolderDive import get_ParentFolderId, Search_Folder, get_folder_name
from DriveFunctions.GetImages import get_image_bytes
from OCRFunctions.TextRecognition import Text_from_images, edit_img, Record_Grouping_with_Dates
from OCRFunctions.OCRCleaner import master_clean_ocr
from ExcelFunctions.OpenExcel import load_in_file, get_column_names
from ExcelFunctions.DataAddition import specific_id_row, row_num_checker, check_row_data, data_per_row
from JSONExtract.JSONtoPy import extract_json
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
from paddleocr import PaddleOCR
import paddle

# Test Updates ================================================================

# =============================================================================

CLIENT_FILE = 'credentials.json'
API_NAME = 'drive'
API_VER = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

filepath = r"G:\\ER Visits(Above 60) - Jan 2020 to Jun 2025.xlsx"

sheet_name= "Visit Recs"

file = load_in_file(filepath= filepath, sheet_name= sheet_name)

column_names = get_column_names(file)

system_content = '''You are a strict medical data extractor. Extract only 
                  what is explicitly present in the text. Never invent or 
                  infer data. If a field is not found, use null.'''

prompt = '''### EXTRACTION RULES:
1. **primary_icd:** Find the "Provisional Diagnosis" table. Identify the single row that has the word "Yes" immediately after "MRD Verified". Extract that row's ICD code and description. If the ICD code appears clean and well-formed (e.g. M17.0, E11.9, J30.9), return it in the format: [Code] [Description]. If the code looks corrupted or garbled, return only the first letter of the code followed by the description (e.g. [M] Bilateral primary osteoarthritis of knee). If no row has "Yes", return null.
2. **other_icd:** From the "Provisional Diagnosis" table, list all rows that do NOT have "Yes" after "MRD Verified". For each, if the ICD code appears clean and well-formed, return the full code. If the code looks corrupted or garbled, return only its first letter. Return as a comma-separated list. Do not include descriptions.
3. **chief_complaint:** Find the FIRST occurrence of "Chief Complaint & History of Present Illness" or "Chief Complaint and History of Present Illness". Extract only the text that comes after "Triage Category: X" within that heading. Stop before "Past History" or any other section heading.
4. **date_of_birth:** Find the text "DOB | Age | Gender:". Extract the value immediately following the label but before the first vertical bar (|). Ensure the date is formatted as DD/MM/YYYY.
5. **nationality:** Find "Nationality:" and return only the nationality value.
6. **Vitals:** Extract temperature, pulse, respiratory rate, BP, and O2 saturation from the FIRST vitals reading only. O2 saturation is the number immediately before or after the first \\% \\symbol in the vitals section.
7. **visit_date / visit_time:** Find the FIRST occurrence of "Visit Date:" followed by DD/MM/YYYY then a 4-digit time. Split into separate fields. If the date separator is missing (e.g. "08/08 2020"), reconstruct it as DD/MM/YYYY.
8. **disposition_date / disposition_time:** Go to the absolute end of the provided text. Search backwards from the very last character until you hit the first date and time pair. This value is likely the discharge/disposition time, from this enter the DD/MM/YYYY for date. Ignore all earlier timestamps found in the Triage or Vitals sections. Ensure the time you extract is specifically the one associated with the end of the patient's visit.
9. **pain_scale_score:** Find the FIRST occurrence of "Numerical(X)". Return only the integer X. Do not confuse with GCS.
10. **gcs:** Find the GCS value in the vitals section. Format is typically XX/15. Return only the numerator.
11. **triage_category:** Find the FIRST occurrence of "Triage Category:" and return only the number after it.
12. **past_history:** Find the FIRST occurrence of "Past History:" or "Past Medical History". Extract only the text directly after it. Stop before "Travel History:". Do not include the label itself.
13. **occupation:** Find the FIRST occurrence of "Occupation:" and extract only the text directly after it.
14. **marital_status:** Find "Marital Status:" and return only the value after it.
15. **advice_health_education:** Find the FIRST occurrence of "Advice & Health Education:" and return only the text immediately after it. Stop at "Education Given To:" or any other label.
16. **condition_at_disposition:** Find "Condition at the time of Disposition:" or "Condition at the tine of Disposition:" and return only the value after it.
17. **disposition_type:** Find "Disposition Type:" and return only the value after it.
18. **remarks:** If remarks text is found after the Provisional Diagnosis table and before the Medication Order table, extract it and correct only obvious OCR spelling errors in individual words while preserving the original sentence structure and word order exactly. Otherwise return null.
19. **travel_history:** Find the FIRST occurrence of "Travel History:". Extract only the text directly after it. Return a value only if it describes a place, country, or region. If the value is a date, month-year, noise, or any non-place text, return null.
20. **current_medication:** Find the FIRST occurrence of "Current Medication". Extract only text directly after it. Stop at "Medical Prescription" or "Medication Order".
21. **psychosocial:** Find the FIRST occurrence of "Psychosocial:" and extract only the text after it. Do not include occupation.
22. **disease_grouping:** Unless specified, leave as null.
'''

paddle.set_flags({
"FLAGS_fraction_of_cpu_memory_to_use": 1.0, # Use 10% of total CPU memory
"FLAGS_allocator_strategy": "naive_best_fit", # Optimize memory fragmentation
"FLAGS_eager_delete_scope": True, # Reduce memory usage by deleting scope synchronously
"FLAGS_eager_delete_tensor_gb": 0.0, # Enable garbage collection
"FLAGS_fast_eager_deletion_mode": True, # Use fast garbage collection
"FLAGS_use_pinned_memory": False, # Disable pinned memory for lower CPU usage
})

ocr_engine = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation= False,
    text_recognition_batch_size=10, 
    precision="fp32",
    text_det_limit_side_len= 4000,
    text_det_limit_type= 'max',
    text_det_box_thresh= 0.3,
    text_det_thresh= 0.2,
    text_det_unclip_ratio=1.6, #Best results with 1.6
    lang='en',
    device= 'cpu',
    enable_mkldnn=True,
    mkldnn_cache_capacity=10,
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
    comp_id = get_folder_name(body= service, folder_id= folder)
    rows= specific_id_row(dataframe= file, specific_id= comp_id)

    image_ids = Search_Folder(body= service, parent_id= folder)

    image_bytes = get_image_bytes(image_file_ids= image_ids)

    readable_img = []
    with ThreadPoolExecutor(max_workers=16) as Executor:
        if image_bytes:
            readable_img = list(Executor.map(edit_img, image_bytes))

    texts = list(Text_from_images(ocr= ocr_engine, readable_list= readable_img))
    print(texts)
    print("OCR done!")
    record = Record_Grouping_with_Dates(texts= texts)
    row_count_check = row_num_checker(rows= rows, total_records= record)
    row_data_check = check_row_data(rows= rows)
    if not row_data_check or not row_count_check:
        new_record = data_per_row(records= record, df= file, comp_id= comp_id)
        print("Cleaning Started!")
        clean_records = master_clean_ocr(records_dict= new_record)
        print(f"\n {clean_records} \n")
        print("LLM processing...")
        llm_step = list(llm_response(llm= llm_engine, clean_records= clean_records, 
                                    column_names= column_names, prompt= prompt, 
                                    system_content= system_content))
        print(llm_step)

        for record in llm_step:
            data = extract_json(llm_output= record)
            print(data)

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Took a total of {elapsed_time:.1f} seconds")