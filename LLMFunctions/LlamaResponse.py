import re

def create_json_template(column_names):
    template = {}
    d = {" ": "_", "/": "", "(": "", ")": "", "&": ""}
    for col in column_names:
        col = re.sub(r"[\s&]|[\(\)\/]", lambda x: d[x[0]], col)
        template[col] = {"type": ["string", "null"]}
    
    return {
        "type": "object",
        "properties": template,
        "required": list(template.keys())
    }


def llm_response(llm, clean_records, prompt, system_content, column_names): # removed json_template for test
    if clean_records:
        schema = create_json_template(column_names)
        for ocr_result in clean_records:
            response = llm.create_chat_completion(
                messages=[
                    {
                        "role":"system",
                        "content":system_content
                    },
                    {
                        "role":"user",
                        "content":f'''{prompt} 
                        ### OUTPUT: 
                        Return ONLY raw JSON. No explanation, no markdown, no 
                        preamble.
                        OCR Text:
                        {ocr_result}'''
                    }
                ],
                response_format={
                    "type": "json_object",
                    "schema": schema
                },
                temperature= 0.7
            )
            output = response["choices"][0]["message"]["content"]
            yield output