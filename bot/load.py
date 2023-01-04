import json
from typing import List

import sqlalchemy.exc
from sqlalchemy.orm import Session

from parse import GoogleSheet, Drive
import create

from transliterate import translit


def elements_students(session: Session, users: List[dict], mainKeys: List[str], groupList: List[str]) -> int:

    names = {user_data.name for user_data in session.query(create.UserData)}

    for user in users:
        params = dict()

        if 'name' in user.keys():
            params['name'] = user['name']
        else:
            raise ValueError(f'Unable to add new user_data '
                             f'because a parameter "name" does not exists.')

        for k in mainKeys:
            if k in user.keys():
                params[k] = user[k]
            else:
                params[k] = None

        for gr in groupList:
            if (gr in user.keys() and user[gr] == "1"):
                params[gr] = True
            else:
                params[gr] = False

        if (params['name'] not in names):  # add user
            session.add(create.UserData(**params))
            names.add(params['name'])

        """
        if 'name' in user.keys():
            params['name'] = user['name']
        else:
            params['name'] = None

        if 'parallel' in user.keys():
            params['parallel'] = user['parallel']
        else:
            params['parallel'] = None

        if 'group' in user.keys():
            params['group'] = user['group']
        else:
            params['group'] = None

        if 'classTeacher' in user.keys():
            params['classTeacher'] = user['classTeacher']
        else:
            params['classTeacher'] = None

        if 'tutor' in user.keys():
            params['tutor'] = user['tutor']
        else:
            params['tutor'] = None
            
        if ('olymp' in user.keys() and user["olymp"] == "+"):
            params['olymp'] = True
        else:
            params['olymp'] = False
            
        if ('noProfOrient' in user.keys() and user["noProfOrient"] == "+"):
            params['noProfOrient'] = True
        else:
            params['noProfOrient'] = False

        if ('etc' in user.keys() and user["etc"] == "+"):
            params['etc'] = True
        else:
            params['etc'] = False

        if ('etc2' in user.keys() and user["etc2"] == "+"):
            params['etc2'] = True
        else:
            params['etc2'] = False

        if (params['name'] not in names):  # add user
            session.add(UserData(**params))
            names.add(params['name'])
        

        else:  # update user
            old_user = session.query(UserData).filter_by(name=params['name']).first()
            old_user.parallel = params['parallel']
            old_user.group = params['group']
            old_user.classTeacher = params['classTeacher']
            old_user.tutor = params['tutor']
            old_user.olymp = params['olymp']
            old_user.noProfOrient = params['noProfOrient']
            old_user.etc = params['etc']
            old_user.etc2 = params['etc2']
        """
    session.commit()
    return 0


def loadDataStudents(session: Session, groupList: List[str], data):
    listData = []
    for v in data.values():
        listData.extend(v)

    users = []
    mainKeys = ["name", "parallel", "group", "classTeacher", "tutor"]
    keys = mainKeys
    keys.extend(groupList)

    for values in listData:
        users.append(dict(zip(keys, values)))

    elements_students(session, users, mainKeys, groupList)


def elements_contents(session: Session, data: dict) -> int:

    google = GoogleSheet()
    types = google.get_types_of_content()
    types_original = types.copy()

    for i in range(len(types)):
        translit_types = translit(types[i], language_code='ru', reversed=True)
        clear = "".join(c for c in translit_types if c.isalpha())
        types[i] = clear

    for group, content in data.items():
        class_name = "".join(c for c in translit(group, language_code='ru', reversed=True) if c.isalpha())


        max_len = 0
        for key, value in content.items():
            if len(value) > max_len:
                max_len = len(value)

        for i in range(max_len):

            params = dict()
            for j in range(len(types)):
                if i >= len(content[types_original[j]]):
                    params[types[j]] = ''
                else:
                    params[types[j]] = content[types_original[j]][i]

            exec(f"session.add(create.{class_name}(**{params}))")

    session.commit()
    return 0


def elements_content(session: Session, data: dict) -> int:

    google = GoogleSheet()
    types = google.get_types_of_content()
    types_original = types.copy()

    for i in range(len(types)):
        translit_types = translit(types[i], language_code='ru', reversed=True)
        clear = "".join(c for c in translit_types if c.isalpha())
        types[i] = clear

    for group, content in data.items():
        params = {}
        class_name = "".join(c for c in translit(group, language_code='ru', reversed=True) if c.isalpha())
        params['group'] = class_name

        for i in range(len(types)):

            params[types[i]] = json.dumps(content[types_original[i]])

        session.add(create.ContentData(**params))

    session.commit()
    return 0


