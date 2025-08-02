import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore

base64_key = os.environ.get("SERVICE_ACCOUNT_KEY_BASE64")

if not base64_key:
    raise ValueError("SERVICE_ACCOUNT_KEY_BASE64 environment variable is not set.")

decoded_key = base64.b64decode(base64_key).decode("utf-8")
service_account_info = json.loads(decoded_key)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()
