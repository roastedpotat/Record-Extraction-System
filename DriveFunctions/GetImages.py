from DriveFunctions.Downloader import DownloadFiles
from concurrent.futures import ThreadPoolExecutor

def get_image_bytes(image_file_ids):
    if image_file_ids:
        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(DownloadFiles, image_file_ids))
            print(f"Done")
            return results
