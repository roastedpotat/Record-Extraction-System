import io
from googleapiclient.http import MediaIoBaseDownload

def DownloadFiles(body: object, ids: list):
    service = body
    file_ids = ids
    count = 1
    total_count = len(file_ids)
    
    for file_id in file_ids:
        request = service.files().get_media(fileId= file_id)

        filecache = io.BytesIO()

        download = MediaIoBaseDownload(fd= filecache, request= request)
        done = False
        
        while not done:
            status, done = download.next_chunk()
            print(f"\n Download {count} / {total_count}")
        count+=1
        filecache.seek(0)
        yield filecache  # Changed filecache.read() into just the filecache obj