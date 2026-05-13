import io
import re
import cv2 as cv
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

def new_edit_image(img_bytes):
    if img_bytes:
        image_bytes = io.BytesIO(img_bytes)
        nparr = np.frombuffer(image_bytes.read(), np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        sharp_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

        resized_img = cv.resize(img, (1920, 1080))
        resized_img = cv.GaussianBlur(resized_img, (7, 7), 0)
        resized_img = cv.filter2D(resized_img, -1, sharp_kernel)
        return resized_img

def edit_img(img_byte):
    if img_byte:
        imgbyte = io.BytesIO(img_byte)
        img = Image.open(imgbyte)

        exif = img.getexif()
        orientation = exif.get(274)

        if orientation is not None and orientation != 1:
            img = ImageOps.exif_transpose(img)
            
        ratio = 2000/max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        resized_img = img.resize(new_size)
        blur_img = resized_img.filter(ImageFilter.GaussianBlur(radius=0.5)) # Old radius = 2
        contrast_img = ImageEnhance.Contrast(blur_img).enhance(2.0) # Old Contrast = 2
        sharp_img = ImageEnhance.Sharpness(contrast_img).enhance(2.5) # Old Sharpness = 1.5 , Best = 2.5
        autocontrast_img = ImageOps.autocontrast(sharp_img, cutoff=3) # Best was either 3 or 4
        readable_img = np.asarray(autocontrast_img)
        img.close()
        return readable_img


def Text_from_images(ocr, readable_list):
    results = ocr.predict_iter(readable_list)
    for item in results:
        texts = item.get('rec_texts', [])
        string = "\n".join(texts)
        yield string

def Record_Grouping_with_Dates(texts):
    record_groups = dict()
    current_key = "Unknown"
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