import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes required for accessing Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Authenticate and create the Gmail service
credentials = authenticate()
service = build('gmail', 'v1', credentials=credentials)

from pymongo import MongoClient

# Establish a connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['python_gmail']
collection = db['gmail_data']


import base64
from googleapiclient.discovery import build

def fetch_emails():
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No emails found.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']
            email_data = {}
            for header in headers:
                name = header['name']
                value = header['value']
                if name.lower() == 'subject':
                    email_data['subject'] = value
                elif name.lower() == 'from':
                    email_data['from'] = value
                elif name.lower() == 'to':
                    email_data['to'] = value

            parts = payload.get('parts', [])
            email_content = ""
            for part in parts:
                if part.get('body'):
                    data = part['body'].get('data')
                    if data:
                        # Decode the data and store the email content
                        decoded_bytes = base64.urlsafe_b64decode(data)
                        email_content += decoded_bytes.decode('utf-8')

            email_data['content'] = email_content

            collection.insert_one(email_data)


fetch_emails()