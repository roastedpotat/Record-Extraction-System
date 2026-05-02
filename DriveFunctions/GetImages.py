from DriveFunctions.Downloader import DownloadFiles
from DriveFunctions.AccessingFolder import *

def get_image_file_ids():
    for folder_id in subfolder_id:
        file_ids = Search_Folder(body= service, parent_id= folder_id)
        yield file_ids

def get_image_bytes():
    for file_ids in get_image_file_ids():
        if file_ids:
            for download_bytes in DownloadFiles(body= service, ids= file_ids):
                yield download_bytes