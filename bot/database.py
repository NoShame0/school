import json

import create
from load import *
import read


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

        add = set()
        delete = set()

        for key, value in list(set(cur.items()) ^ set(cur.items())):
            if key in new and new[key] == value:
                if key not in cur:
                    add.add((key, value))
                else:
                    new_content = list(set(value) - set(cur[key]))
                    old_content = list(set(cur[key]) - set(value))
                    add.add((key, new_content))
                    delete.add((key, old_content))
            else:
                delete.add((key, value))

        diff = {
            'add': dict(add),
            'delete': dict(delete),
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

        loadDataStudents(self.session, groupList, data)

    def load_to_base_content(self):

        self.session.query(create.ContentData).delete(synchronize_session='fetch')
        self.session.commit()

        elements_content(self.session, self.google_sheet.read_data_content())

    def read_info_students(self, **params):
        return [(student['name'], student['parallel'], student['group'], student['group_category']) for student in read.elements_students(
            self.session, **params)]

    def read_info_content(self, **params):
        return read.elements_content(self.session, **params)



