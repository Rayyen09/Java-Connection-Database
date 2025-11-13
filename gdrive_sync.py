"""
Google Drive Sync Module
Modul untuk menyimpan dan memuat data dari Google Drive
"""

import os
import json
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile

class GDriveSync:
    """Class untuk mengelola sinkronisasi data dengan Google Drive"""

    def __init__(self):
        self.drive = None
        self.folder_id = None
        self.enabled = False
        self.init_drive()

    def init_drive(self):
        """Initialize Google Drive connection"""
        try:
            # Check if credentials exist
            if not os.path.exists('credentials.json'):
                st.warning("⚠️ Google Drive sync tidak aktif. Upload credentials.json untuk mengaktifkan.")
                return

            # Authenticate
            gauth = GoogleAuth()

            # Try to load saved client credentials
            if os.path.exists('token.pickle'):
                gauth.LoadCredentialsFile('token.pickle')

            if gauth.credentials is None:
                # Authenticate if they're not there
                # Use settings.yaml for authentication flow
                if os.path.exists('settings.yaml'):
                    gauth.LocalWebserverAuth()
                else:
                    st.error("❌ settings.yaml tidak ditemukan. Silakan setup Google Drive API.")
                    return
            elif gauth.access_token_expired:
                # Refresh them if expired
                gauth.Refresh()
            else:
                # Initialize the saved creds
                gauth.Authorize()

            # Save credentials
            gauth.SaveCredentialsFile('token.pickle')

            # Create drive instance
            self.drive = GoogleDrive(gauth)

            # Get or create app folder
            self.folder_id = self._get_or_create_folder('PPIC_DSS_Data')
            self.enabled = True

        except Exception as e:
            st.error(f"❌ Error menginisialisasi Google Drive: {e}")
            self.enabled = False

    def _get_or_create_folder(self, folder_name):
        """Get or create folder in Google Drive"""
        try:
            # Search for folder
            file_list = self.drive.ListFile({
                'q': f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            }).GetList()

            if file_list:
                return file_list[0]['id']
            else:
                # Create folder
                folder_metadata = {
                    'title': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.drive.CreateFile(folder_metadata)
                folder.Upload()
                return folder['id']
        except Exception as e:
            st.error(f"Error creating/finding folder: {e}")
            return None

    def upload_file(self, local_path, filename=None):
        """Upload file to Google Drive"""
        if not self.enabled or not self.drive:
            return False

        try:
            if filename is None:
                filename = os.path.basename(local_path)

            # Check if file already exists
            file_list = self.drive.ListFile({
                'q': f"title='{filename}' and '{self.folder_id}' in parents and trashed=false"
            }).GetList()

            if file_list:
                # Update existing file
                file_drive = file_list[0]
                file_drive.SetContentFile(local_path)
                file_drive.Upload()
            else:
                # Create new file
                file_drive = self.drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': self.folder_id}]
                })
                file_drive.SetContentFile(local_path)
                file_drive.Upload()

            return True
        except Exception as e:
            st.error(f"Error uploading {filename}: {e}")
            return False

    def download_file(self, filename, local_path):
        """Download file from Google Drive"""
        if not self.enabled or not self.drive:
            return False

        try:
            # Search for file
            file_list = self.drive.ListFile({
                'q': f"title='{filename}' and '{self.folder_id}' in parents and trashed=false"
            }).GetList()

            if file_list:
                file_drive = file_list[0]
                file_drive.GetContentFile(local_path)
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Error downloading {filename}: {e}")
            return False

    def sync_to_drive(self, files_to_sync):
        """Sync multiple files to Google Drive"""
        if not self.enabled:
            return False

        success_count = 0
        for file_path in files_to_sync:
            if os.path.exists(file_path):
                if self.upload_file(file_path):
                    success_count += 1

        return success_count == len(files_to_sync)

    def sync_from_drive(self, files_to_download):
        """Download multiple files from Google Drive"""
        if not self.enabled:
            return False

        success_count = 0
        for filename, local_path in files_to_download.items():
            if self.download_file(filename, local_path):
                success_count += 1

        return success_count > 0


# Singleton instance
_gdrive_sync = None

def get_gdrive_sync():
    """Get or create GDrive sync instance"""
    global _gdrive_sync
    if _gdrive_sync is None:
        _gdrive_sync = GDriveSync()
    return _gdrive_sync
