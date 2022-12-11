import json
from typing import List
from sqlalchemy.orm import Session, sessionmaker

from parse import GoogleSheet
from create import UserData


def elements(session: Session, users: List[dict]) -> int:

    names = {user_data.name for user_data in session.query(UserData)}

    for user in users:
        params = dict()

        if 'name' in user.keys():
            params['name'] = user['name']
        else:
            raise ValueError(f'Unable to add new user_data '
                             f'because a parameter "name" does not exists.')

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

    session.commit()
    return 0


def loadData(session):    
    googleSheet = GoogleSheet()
    data = googleSheet.read_data()

    listData = []
    for v in data.values():
        listData.extend(v)

    users = []
    keys = ["name", "parallel", "group", "classTeacher", "tutor", "olymp", "noProfOrient", "etc", "etc2"]
    for values in listData:
        users.append(dict(zip(keys, values)))
    
    elements(session, users)


    