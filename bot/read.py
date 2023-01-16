from typing import List
from sqlalchemy.orm import Session
import create
import json


def elements_students(
    session: Session,
    name="",
    parallel="",
    group="",
    class_teacher="",
    tutor="",
) -> List[dict]:

    params = dict()

    if name != "":
        params["name"] = name

    if parallel != "":
        params["parallel"] = parallel

    if group != "":
        params["group"] = group

    if class_teacher != "":
        params["classTeacher"] = class_teacher

    if tutor != "":
        params["tutor"] = tutor

    users_data = []
    for user_data in session.query(create.UserData).filter_by(**params):

        user = {
            "name": user_data.name,
            "parallel": user_data.parallel,
            "group": user_data.group,
            "classTeacher": user_data.classTeacher,
            "tutor": user_data.tutor,
            'group_category': []
        }

        for atr in create.UserData.groupList:
            if getattr(user_data, atr):
                user['group_category'].append(atr)

        users_data.append(user)

    return users_data


def elements_content(
    session: Session,
    group="",
) -> dict:

    params = {}
    if group != '':
        params['group'] = group

    result = {}
    for content_data in session.query(create.ContentData).filter_by(**params):
        result[content_data.group] = {}
        for type in create.types:
            exec(f"result[content_data.group]['{type}'] = json.loads(content_data.{type})")

    return result


def check_password(session: Session, name: str, password: str) -> bool:
    admin = session.query(create.AdminData).filter_by(name=name).first()
    return admin.check_password(password)


if __name__ == "__main__":
    import create, load

    print(elements_content(create.create_session()))
    #s = create.create_session()
    #load.elements_admin(session=s, name="ya", password="admin")
    #print(check_password(session=s, name="ya", password="p"))
