from __future__ import print_function

import data
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import requests
import pickle


def get_syms_by_num(number):
    result = ""

    while number > 0:
        result = chr(ord('A') + (number - 1) % 26) + result
        number = (number - 1) // 26

    return result


#   The class is necessary for working with the table (writing and reading information)
class GoogleSheet:

    # __init__ this is an example from the Google Sheets API documentation
    SPREADSHEET_ID = data.SPREADSHEET_ID
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    service = None

    def __init__(self):

        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

        self.sheets_info = None
        self.info()

        self.creds = creds

    def read_data(self):

        lists_parallel = {}

        for sheet in self.sheets_info['sheets']:

            title = sheet['properties']['title']
            group_count = len(self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                                       range="2:2").execute().get('values', [])[0]) - 5

            users_info = self.service.spreadsheets()\
                .values().get(spreadsheetId=self.SPREADSHEET_ID,
                              range=title + '!A3:' + get_syms_by_num(5 + group_count)).execute()

            users_info = users_info.get('values', [])
            lists_parallel[title] = users_info

        return lists_parallel

    def _on_edit(self):
        return self.service.spreadsheets().get(spreadsheetId=self.SPREADSHEET_ID).execute()

    def info(self):

        self.sheets_info = self.service.spreadsheets()\
            .get(spreadsheetId=self.SPREADSHEET_ID, fields='sheets.properties')\
            .execute()

    def get_groups_of_students(self):
        return self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                                       range="F2:2").execute().get('values', [])[0]

if __name__ == "__main__":
    print(GoogleSheet().get_groups_of_students())
