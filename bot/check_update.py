import datetime
import time
import threading

import data
import parse


def convert_date_from_google_drive(time_str: str):

    cur_time = time_str.split('.')[0]
    cur_time = datetime.datetime.strptime(cur_time, "%Y-%m-%dT%H:%M:%S")
    return cur_time


class TimeChecker:

    def __init__(self, database):

        self.database = database

        self.drive = parse.Drive()
        self.last_time_update_students = convert_date_from_google_drive(
            self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))

        self.last_time_update_contents = convert_date_from_google_drive(
            self.drive.get_modified_date(data.SPREADSHEET_CONTENTS_ID))

    def time_check(self):
        # infinity loop for checkin user time last message
        while True:
            cur_time_update_students = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))

            cur_time_update_contents = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_CONTENTS_ID))

            if cur_time_update_students > self.last_time_update_students:
                self.last_time_update_students = cur_time_update_students
                self.database.load_to_base_students()

            if cur_time_update_contents > self.last_time_update_contents:
                self.last_time_update_students = cur_time_update_contents
                self.database.load_to_base_content()

            time.sleep(60)

    def start(self):

        thread = threading.Thread(target=self.time_check)
        thread.start()
