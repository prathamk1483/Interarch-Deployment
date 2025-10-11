import os
import logging
from django.conf import settings
from urllib.parse import quote  # for URL-encoding

logger = logging.getLogger(__name__)

def upload_file(file_obj, filename=None, clientName=None, folder_id=None, folder_name=None):
    """
    Save file locally to a specific folder and return its URL relative to MEDIA_URL.
    """

    # Determine final filename
    final_filename = filename or getattr(file_obj, "name", "unnamed_file")

    # Determine folder to save the file
    base_folder = getattr(settings, "LOCAL_UPLOAD_FOLDER", "uploads")  # default uploads
    target_folder = os.path.join(base_folder, clientName or folder_name or "")
    os.makedirs(target_folder, exist_ok=True)  # create folder if it doesn't exist

    # Full path to save the file
    file_path = os.path.join(target_folder, final_filename)

    print(f"--- DEBUG: Starting local save for {final_filename} at {file_path} ---")  # Force console log

    try:
        # Write file content to local folder
        with open(file_path, "wb") as f:
            for chunk in file_obj.chunks() if hasattr(file_obj, "chunks") else [file_obj.read()]:
                f.write(chunk)

        # Construct URL relative to MEDIA_URL
        relative_folder = os.path.relpath(target_folder, getattr(settings, "MEDIA_ROOT", base_folder))
        # URL encode folder and filename to handle spaces/special chars
        url = f"{settings.MEDIA_URL}{quote(relative_folder)}/{quote(final_filename)}"
        print(f"--- DEBUG: Local save success for {final_filename}, URL={url} ---")  # Force console log
        return f"{settings.MEDIA_URL}/{quote(relative_folder)}"

    except Exception as e:
        print(f"--- DEBUG: Local save failed for {final_filename}: {e} ---")  # Force console log
        logger.error(f"Failed to save '{final_filename}' locally: {e}", exc_info=True)
        return None
