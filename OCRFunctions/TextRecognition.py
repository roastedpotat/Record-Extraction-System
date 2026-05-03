import io
import re
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from numpy import asarray

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