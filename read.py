import json
from typing import List, Optional
from sqlalchemy.orm import Session
from transliterate import translit
import create
import parse


def elements(
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
        }
        for atr in create.UserData.groupList:
            user[atr] = getattr(user_data, atr)

        users_data.append(user)

    return users_data


if __name__ == '__main__':
    elements(create.create_session())
