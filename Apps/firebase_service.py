# app/firebase_service.py

import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate("serviceAccountKey.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://ecotrackai-7a140-default-rtdb.asia-southeast1.firebasedatabase.app/"
        },
    )


def update_relay_state(relay_key: str, state: bool):
    ref = db.reference(f"relays/{relay_key}")
    ref.update({"state": state})