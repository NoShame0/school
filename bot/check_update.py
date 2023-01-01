import datetime
import time
import threading

import data
import parse
import load


def convert_date_from_google_drive(time_str: str):

    cur_time = time_str.split('.')[0]
    cur_time = datetime.datetime.strptime(cur_time, "%Y-%m-%dT%H:%M:%S")
    return cur_time


class TimeChecker:

    def __init__(self):

        self.drive = parse.Drive()
        self.last_time_update = convert_date_from_google_drive(
            self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))

    def time_check(self):
        # infinity loop for checkin user time last message
        while True:
            cur_time_update = convert_date_from_google_drive(self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))
            if cur_time_update > self.last_time_update:
                load.main_load()
                self.last_time_update = cur_time_update

            time.sleep(60)

    def start(self):

        thread = threading.Thread(target=self.time_check)
        thread.start()
