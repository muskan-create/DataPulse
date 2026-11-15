import os
import secrets


# Base Directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# Secret Key
SECRET_KEY = os.environ.get(
    "DATAPULSE_SECRET_KEY"
) or secrets.token_hex(32)


# Upload Configuration
UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "csv",
    "xlsx",
    "xls"
}


# Maximum Upload Size: 20 MB
MAX_CONTENT_LENGTH = 20 * 1024 * 1024


# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False


# Create Upload Folder
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)