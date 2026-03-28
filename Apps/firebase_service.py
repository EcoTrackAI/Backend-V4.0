import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db


DEFAULT_DATABASE_URL = (
    "https://ecotrackai-7a140-default-rtdb.asia-southeast1.firebasedatabase.app/"
)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SERVICE_ACCOUNT_PATH = PROJECT_ROOT / "serviceAccountKey.json"


def _build_credential():
    credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if credentials_json:
        try:
            return credentials.Certificate(json.loads(credentials_json))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid FIREBASE_CREDENTIALS_JSON") from exc

    if credentials_path:
        return credentials.Certificate(credentials_path)

    if DEFAULT_SERVICE_ACCOUNT_PATH.exists():
        return credentials.Certificate(str(DEFAULT_SERVICE_ACCOUNT_PATH))

    # Allows cloud runtimes with default credentials.
    return None


def initialize_firebase() -> None:
    if firebase_admin._apps:
        return

    database_url = os.getenv("FIREBASE_DATABASE_URL", DEFAULT_DATABASE_URL)
    options = {"databaseURL": database_url}
    credential = _build_credential()

    if credential is not None:
        firebase_admin.initialize_app(credential, options)
        return

    firebase_admin.initialize_app(options=options)


def update_relay_state(relay_key: str, state: bool) -> None:
    initialize_firebase()
    ref = db.reference(f"relays/{relay_key}")
    ref.update({"state": state})