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

        for class_name in create.groups:
            exec(f"self.session.query(create.{class_name}).delete(synchronize_session='fetch')")

        self.session.commit()

        elements_contents(self.session, self.google_sheet.read_data_content())

    def read_info_students(self):
        return [(student['name'], student['parallel'], student['group']) for student in read.elements_students(
            self.session)]

    def read_info_content(self):
        pass

