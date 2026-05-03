from DriveFunctions.Google import Create_Service

CLIENT_FILE = 'credentials.json'
API_NAME = 'drive'
API_VER = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def DownloadFiles(id):
    test = Create_Service(CLIENT_FILE, API_NAME, API_VER, SCOPES)
    request = test.files().get_media(fileId= id).execute()
    return request