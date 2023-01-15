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

        self.end = False

    def time_check(self):

        while not self.end:
            cur_time_update_students = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_STUDENTS_ID))

            cur_time_update_contents = convert_date_from_google_drive(
                self.drive.get_modified_date(data.SPREADSHEET_CONTENTS_ID))

            if cur_time_update_students > self.last_time_update_students:

                    print("Таблица со студентами изменена")
                    print("Загрузка бд...")

                    self.database.load_to_base_students()

                    new_students_info = self.database.read_info_students()
                    cur_chats_info = self.database.read_chats_info()

                    update_info = {}
                    for chat_id, info in cur_chats_info.items():

                        new_info = info.copy()

                        for student in new_students_info:
                            if info['name'] == student[0] and info['class_group'] == str(student[1]) + student[2]:
                                new_info['group'] = student[3]
                                break

                        update_info[chat_id] = new_info

                    self.database.chats_update(update_info)

                    self.last_time_update_students = cur_time_update_students
                    print("Загрузка бд завершена")
                    self._students_updated = True

            if cur_time_update_contents > self.last_time_update_contents:
                try:
                    print("Таблица с конетентом изменена")
                    self.last_time_update_contents = cur_time_update_contents
                    print("Загрузка бд....")
                    self.database.load_to_base_content()
                    print("Загрузка бд завершена")
                    self._content_updated = True
                except:
                    print("Не удалось обновить контент")

            time.sleep(15)
        return 0

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

        thread = threading.Thread(target=self.time_check, daemon=True)
        thread.start()
