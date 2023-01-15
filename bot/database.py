import json

import sqlalchemy
import create
import load
import read
from parse import GoogleSheet
from transliterate import translit


class DataBase:

    def __init__(self):

        self.session = create.create_session()

        try:
            create.create()
        except sqlalchemy.exc.ProgrammingError:
            self.clear_base()

        self.google_sheet = GoogleSheet()

        self.load_to_base_students()
        self.load_to_base_content()
        self.students = self.read_info_students()
        self.content = self.read_info_content()

    def update_content(self):
        cur = self.content
        new = self.read_info_content()

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

        load.elements_content(self.session, self.google_sheet.read_data_content())

    def read_info_students(self, **params):
        return [(student['name'], student['parallel'], student['group'], student['group_category']) for student in
                read.elements_students(
                    self.session, **params)]

    def read_info_content(self, **params):
        return read.elements_content(self.session, **params)

    def chats_update(self, params: dict):

        params_copy = dict(params)

        for chat_id in params_copy.keys():

            params_copy[chat_id]['group'] = json.dumps(params_copy[chat_id]['group'])

            query = self.session.query(create.ChatData).filter_by(chat_id=chat_id)
            if list(query):
                query.update(params_copy[chat_id], synchronize_session='fetch')
            else:
                params_copy[chat_id]['chat_id'] = chat_id

                self.session.add(create.ChatData(**(params_copy[chat_id])))

        self.session.commit()

    def read_chats_info(self, **params):

        query = self.session.query(create.ChatData).filter_by(**params)

        result = {}
        for chat_data in query:
            result[chat_data.chat_id] = {
                "start": chat_data.start,
                "name": chat_data.name,
                "register": chat_data.register,
                "group": json.loads(chat_data.group),
                "status": chat_data.status,
                "class_group": chat_data.class_group,
            }

        return result

    def clear_base(self):
        self.session.query(create.ContentData).filter_by().delete()
        self.session.commit()


if __name__ == "__main__":
    db = DataBase()

    db.clear_base()
