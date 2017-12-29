import os
from firebase_admin import credentials, initialize_app, db

firebase_config = {
    "projectId": "tembotest",
    "databaseURL": "https://tembotest.firebaseio.com",
}

PRIVATE_PATH = os.path.join(os.getcwd(), "private")
SERVICE_KEY_PATH = os.path.join(PRIVATE_PATH, "tembotest-firebase-adminsdk.json")
CRED = credentials.Certificate(SERVICE_KEY_PATH)
initialize_app(CRED, firebase_config)


