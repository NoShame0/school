from __future__ import print_function

from bot import data
import os.path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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
    SPREADSHEET_STUDENTS_ID = data.SPREADSHEET_STUDENTS_ID
    SPREADSHEET_CONTENTS_ID = data.SPREADSHEET_CONTENTS_ID

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

        self.creds = creds

    def read_data_students(self):

        lists_parallel = {}

        self.info(self.SPREADSHEET_STUDENTS_ID)

        for sheet in self.sheets_info['sheets']:

            title = sheet['properties']['title']
            group_count = len(self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_STUDENTS_ID,
                                                                       range="2:2").execute().get('values', [])[0]) - 5

            users_info = self.service.spreadsheets()\
                .values().get(spreadsheetId=self.SPREADSHEET_STUDENTS_ID,
                              range=title + '!A3:' + get_syms_by_num(5 + group_count)).execute()

            users_info = users_info.get('values', [])
            lists_parallel[title] = users_info

        return lists_parallel

    def read_data_content(self):

        content_groups = {}
        self.info(self.SPREADSHEET_CONTENTS_ID)
        for sheet in self.sheets_info['sheets']:
            content_group = {}
            title = sheet['properties']['title']

            types = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_CONTENTS_ID,
                                                               range="2:2").execute().get('values', [])[0]
            col = 1
            for type in types:
                range = title + '!' + get_syms_by_num(col) + '3:' + get_syms_by_num(col)
                content_group[type] = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_CONTENTS_ID,
                         range=range).execute().get('values', [])

                if content_group[type]:
                    content_group[type] = content_group[type][0]
                col += 1

            content_groups[title] = content_group

        return content_groups


    def _on_edit(self):
        pass

    def info(self, SPREADSHEET_ID):

        self.sheets_info = self.service.spreadsheets()\
            .get(spreadsheetId=SPREADSHEET_ID, fields='sheets.properties')\
            .execute()

    def get_groups_of_students(self):
        return self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_STUDENTS_ID,
                                                        range="F2:2").execute().get('values', [])[0]

    def get_types_of_content(self):

        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_CONTENTS_ID,
                                                        range="A2:2").execute().get('values', [])
        if result:
            return result[0]
        return result

if __name__ == "__main__":
    print(GoogleSheet().get_types_of_content())
