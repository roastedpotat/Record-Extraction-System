from OCRFunctions.OCRCleaner import clean_ocr
import pickle

import pickle
import os

CACHE_FILE = "data_cache.pkl"

if os.path.exists(CACHE_FILE):
    # Load the object from disk
    with open(CACHE_FILE, "rb") as f:
        my_object = pickle.load(f)
        print(len(my_object))
        print(my_object)
    print("Loaded from cache")
else:
    x=[]
    # Perform the expensive operation
    for my_object in clean_ocr():
        ocr = " ".join(my_object)
        x.append(ocr)
    # Save the object for next time
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(x, f)
    print("Computed and cached")
