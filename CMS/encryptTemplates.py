import os
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Adjust this to your templates folder(s)
TEMPLATE_DIRS = [
    Path("templates/CRUDmodule"),  # no need for './'
]

KEY = os.environ.get("TEMPLATE_KEY")
if not KEY:
    raise SystemExit("Set TEMPLATE_KEY environment variable before running this script")

fernet = Fernet(KEY.encode())

def encrypt_file(path: Path):
    """Encrypt a single .html file to .html.enc"""
    data = path.read_bytes()
    enc = fernet.encrypt(data)
    out = path.with_suffix(path.suffix + ".enc")  # file.html -> file.html.enc
    out.write_bytes(enc)
    print(f"✅ Encrypted: {path}  →  {out}")

for d in TEMPLATE_DIRS:
    if not d.exists():
        print(f"⚠️  Template directory not found: {d}")
        continue

    for p in d.rglob("*.html"):
        encrypt_file(p)
