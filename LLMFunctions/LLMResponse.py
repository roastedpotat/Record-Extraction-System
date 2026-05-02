from OCRFunctions.OCRCleaner import clean_ocr
from ExcelFunctions.JSONTemplate import create_template
import ollama

def llm_response():
    json_template = create_template()
    prompt =f'''

             '''
    system_content = ('''You are a strict medical data extractor. Extract only 
                      what is explicitly present in the text. Never invent or 
                      infer data. If a field is not found, use null.''')
    for ocr_results in clean_ocr():
        ocr_results = " ".join(ocr_results)
        print("LLM Process Ongoing...")
        response = ollama.chat(model= 'qwen2.5:7b',
                               options= {
                                   'num_ctx': 6144, 
                                   'temperature': 0, 
                                   'num_predict': 1024, 
                                   'num_threads': 8
                                   }, 
                                   messages=[{
                                       'role': 'system',
                                       'content': f'{system_content}'
                                       },
                                       {
                                           'role': 'user',
                                           'content': f'''{prompt} 
                                           ### OUTPUT: Return ONLY raw JSON. 
                                             No explanation, no markdown, 
                                             no preamble. 
                                             OCR Text: 
                                             {ocr_results} 
                                             REQUIRED JSON TEMPLATE: 
                                             {json_template}'''}],
                                             format= 'json')
        answer = response.message.content
        yield answer