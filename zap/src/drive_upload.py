#!/usr/bin/env python3
"""
Helper functions for connecting to, navigating, and uploading to Google Drive.
"""
import logging
import calendar
from calendar import WEDNESDAY
from datetime import timedelta
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build



def find_children(parent_id, files):
    """
    Helper function for building out the directory tree of
    google drive folders.
    """
    children = []
    for file in files:
        # In Drive API Parents is always a list with up to one member
        working_id = file.get('parents')[0] if (file.get('parents') is not None) else ""
        if working_id == parent_id:
            # build child dict
            child = {'id':file.get('id'),
                        'name':file.get('name'),
                        'parents':file.get('parents'),
                        'children':[]}

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

def get_folders(drive_service, drive_id, page_token = None):
    """
    Returns all available folders in a specified shared drive.
    """
    response = (
          drive_service.files()
          .list(
              q="mimeType='application/vnd.google-apps.folder'",
              spaces="drive",
              fields="nextPageToken, files(id, name, parents)",
              includeItemsFromAllDrives=True,
              supportsAllDrives=True,
              driveId=drive_id,
              corpora="drive",
              pageToken=page_token,
          )
          .execute()
      )
    return response.get("files"), response.get("nextPageToken")


def get_folders_with_structure(root_id, drive_id, drive_service):
    """
    Takes in a list of files and returns a dict that mimics
    the directory structure in google drive.
    """
    files, next_page_token = get_folders(drive_service, drive_id)
    while next_page_token:
        page, next_page_token = get_folders(drive_service, drive_id, next_page_token)
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
    if len(folder_structure) < 1:
        return None

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
        if target_folder:
            break
    return target_folder


def upload_file_to_drive(filename, folder_id, drive_id, drive):
    """
    Uploads a specific file to a specific folder in google drive.
    """
    media = MediaFileUpload(filename)
    parents = []
    parents.append(folder_id)
    file_metadata = {
            'name': filename,
            'parents': parents,
            'driveId': drive_id
        }
    file = drive.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id',
                                    supportsAllDrives=True).execute()
    return file

def after_fourth_wednesday(date):
    """
    Returns true if is the fourth Wednesday of the month or later.
    """
    _,day_count = calendar.monthrange(date.year, date.month)
    current_weekday = date.weekday()
    current_day = date.day
    offset = (current_weekday - WEDNESDAY) % 7
    previous_wednesday = date - timedelta(days=offset)
    # How far from the end of the month are we.
    diff = day_count - current_day
    # If it's not the last ten days of the month, return False.
    if diff > (day_count-21):
        return False
    # The earliest day the 4th wednesday can be is the 22nd.
    diff = previous_wednesday.day - 21
    if diff > 0:
        return True
    return False
