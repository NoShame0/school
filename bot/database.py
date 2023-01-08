import json

import sqlalchemy
import create
import load
import read
from parse import GoogleSheet
from transliterate import translit


class DataBase:

    def __init__(self):

        try:
            create.create()
        except sqlalchemy.exc.ProgrammingError:
            pass

        self.session = create.create_session()
        self.google_sheet = GoogleSheet()

        self.load_to_base_students()
        self.load_to_base_content()
        self.students = self.read_info_students()
        self.content = self.read_info_content()

    def update_content(self):
        cur = self.content
        new = self.read_info_content()

        print(cur == new)

        add = {}

        for group, content in new.items():
            if group in cur:
                if cur[group].items() == content.items():
                    print("Таблица", group, "не изменена")
                else:
                    add[group] = {}
                    for type_content, links in content.items():
                        if type_content in cur[group]:
                            if cur[group][type_content] == links:
                                print("Контент", group, type_content, "не изменен")
                            else:
                                print("Контент", group, type_content, "изменен")
                                add[group][type_content] = list(set(links) - set(cur[group][type_content]))

        diff = {
            'add': add,
        }

        self.content = new

        return diff

    def load_to_base_students(self):

        self.session.query(create.UserData).delete(synchronize_session='fetch')
        self.session.commit()

        ruGroupList = self.google_sheet.get_groups_of_students()
        data = self.google_sheet.read_data_students()
        groupList = []

        # транслит + очистка строки от лишних символов
        for gr in ruGroupList:
            translitGr = translit(gr, language_code='ru', reversed=True)
            clearGr = "".join(c for c in translitGr if c.isalpha())
            groupList.append(clearGr)

        load.loadDataStudents(self.session, groupList, data)

    def load_to_base_content(self):

        self.session.query(create.ContentData).delete(synchronize_session='fetch')
        self.session.commit()

        load.elements_content(self.session, self.google_sheet.read_data_content())

    def read_info_students(self, **params):
        return [(student['name'], student['parallel'], student['group'], student['group_category']) for student in read.elements_students(
            self.session, **params)]

    def read_info_content(self, **params):
        return read.elements_content(self.session, **params)
