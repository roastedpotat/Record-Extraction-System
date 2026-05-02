import os
import re
from PIL import Image, ImageEnhance, ImageFilter
from numpy import asarray
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
from paddleocr import PaddleOCR
from DriveFunctions.GetImages import get_image_bytes

def Text_from_images():
# OCR Engine:
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        lang='en',
        device='cpu',
        enable_mkldnn=True,
        cpu_threads=8,
        rec_batch_num=10,
        )
# Image to be processed:
    for img_byte in get_image_bytes():
        img = Image.open(img_byte)

        ratio = 2500/max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        resized_img = img.resize(new_size)
        #New additions:
        contrast_img = ImageEnhance.Contrast(resized_img).enhance(2.0)
        sharp_img = ImageEnhance.Sharpness(contrast_img).enhance(1.5)

        readable_img = asarray(sharp_img)
# Text Recognition:
        string = ""
        results = ocr.predict(readable_img)
        for item in results[0]['rec_texts']:
            string+=item + " "
        img_byte.close() # Added a manual image close function!
        yield string

def Record_Grouping_with_Dates():
    record_groups = dict()
    current_key = None
    for records in Text_from_images():
        query = r"Visit Date[\W|\w\s]\s?(\d{2})[\W|\w\s]\s?(\d{2})[\W|\w\s]\s?(\d{4})"
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
