from DriveFunctions.Google import Create_Service
from DriveFunctions.FolderDive import get_ParentFolderId, Search_Folder

CLIENT_FILE = 'credentials.json'
API_NAME = 'drive'
API_VER = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

service = Create_Service(CLIENT_FILE, API_NAME, API_VER, SCOPES)

parent_folder_id = get_ParentFolderId(body= service, 
                                      text= 'Test UploadFolder')
# These subfolders are named with each comp ID:
subfolder_id = Search_Folder(body= service, parent_id= parent_folder_id)