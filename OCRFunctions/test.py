import time
start_time = time.perf_counter()
from OCRFunctions.OCRCleaner import clean_ocr

for x in clean_ocr():
    x = " ".join(x)
    print(f"\n Cleaned OCR results are: \n {x}")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Total time taken is {elapsed_time:.1f} seconds")