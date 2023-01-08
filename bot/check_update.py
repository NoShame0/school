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

        self._content_updated = False
        self._students_updated = False

    def time_check(self):

        while True:
            cur_time_update_students = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))

            cur_time_update_contents = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_CONTENTS_ID))

            if cur_time_update_students > self.last_time_update_students:
                print("Таблица со студентами изменена")
                self.last_time_update_students = cur_time_update_students
                print("Загрузка бд")
                self.database.load_to_base_students()
                print("Загрузка бд")
                self._students_updated = True

            if cur_time_update_contents > self.last_time_update_contents:
                print("Таблица с конетентом изменена")
                self.last_time_update_contents = cur_time_update_contents
                print("Загрузка бд....")
                self.database.load_to_base_content()
                print("Загрузка бд завершена")
                self._content_updated = True

            time.sleep(60)

    def content_is_updated(self):

        result = self._content_updated
        if result:
            print("Изменение контента замечено")
        self._content_updated = False
        return result

    def students_is_updated(self):
        print("Изменение студентов замечено")
        result = self._students_updated
        self._students_updated = False
        return result

    def start(self):

        thread = threading.Thread(target=self.time_check)
        thread.start()
