import logging


import google.auth
import datetime
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build


def find_children(parent_id, files):
    """
    Helper function for building out the directory tree of
    google drive folders.
    """
    print('recurse!')
    children = []
    for file in files:
        # In Drive API Parents is always a list with up to one member
        working_id = file.get('parents')[0] if (file.get('parents') is not None) else ""
        print(working_id)
        if working_id == parent_id:
            # build child dict
            child = {'id':file.get('id'),
                        'name':file.get('name'),
                        'parents':file.get('parents'),
                        'children':[]}
            # A file can only have one parent, so we can remove it from our search list.
            files.remove(file)

            offspring = find_children(child['id'], files)
            for grandchild in offspring:
                child['children'].append(grandchild)
            children.append(child)

    return children


def get_drive_service():
    """
    Connects to google apis, and returns an object for
    connection to google drive.
    """
    logging.info('Connecting to Google Drive.')

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    credentials.refresh(GoogleAuthRequest())

    service = build('drive', 'v3', credentials=credentials)
    return service

def get_folders(drive_service, page_token = None):
    """
    Returns all available folders in a user's drive.
    """
    logging.info("Pulling folder names from Google Drive.")
    response = (
          drive_service.files()
          .list(
              q="mimeType='application/vnd.google-apps.folder'",
              spaces="drive",
              fields="nextPageToken, files(id, name, parents)",
              pageToken=page_token,
          )
          .execute()
      )   
    return response.get("files"), response.get("nextPageToken")


def get_folders_with_structure(root_id, drive_service):
    """
    Takes in a list of files and returns a dict that mimics
    the directory structure in google drive.
    """
    files, next_page_token = get_folders(drive_service)
    while next_page_token:
        page, next_page_token = get_folders(drive_service, next_page_token)
        files.extend(page)

    folder_structure = {}
    for file in files:
        if file["id"] == root_id:
            logging.info("Root folder has been found.")
            folder_structure["id"] = file["id"]
            folder_structure["name"] = file["name"]
            folder_structure["children"] = []
            files.remove(file)
            break

    offspring = find_children(folder_structure['id'], files)
    for grandchild in offspring:
        folder_structure['children'].append(grandchild)
    return folder_structure


def find_subfolder(folder_structure, target_name, target_folder=None):
    """
    Finds a specific subfolder by name, returns the dict for that folder.
    """
    for child in folder_structure['children']:
        if child['name'] == target_name:
            target_folder = child
            return target_folder

        target_folder = find_subfolder(child, target_name)
    return target_folder


def upload_file_to_drive(filename, folder_id, drive):
    """
    Uploads a specific file to a specific folder in google drive.
    """
    media = MediaFileUpload(filename)
    parents = []
    parents.append(folder_id)
    file_metadata = {
            'name': 'notarealscan.xml',
            'parents': parents
        }
    file = drive.files().create(body=file_metadata, media_body=media,
                                     fields='id').execute()
    return file