import json
from typing import List, Optional
from sqlalchemy.orm import Session


import create


def elements(
    session: Session,
    name="",
    parallel="",
    group="",
    classTeacher="",
    tutor="",
    etc="",
    etc2="",
) -> List[dict]:

    params = dict()

    if name != "":
        params["name"] = name

    if parallel != "":
        params["parallel"] = parallel

    if group != "":
        params["group"] = group

    if classTeacher != "":
        params["classTeacher"] = classTeacher

    if tutor != "":
        params["tutor"] = tutor
        
    if etc != "":
        params["etc"] = etc

    if etc2 != "":
        params["etc2"] = etc2

    users_data = [
        {
            "name": user_data.name,
            "parallel": user_data.parallel,
            "group": user_data.group,
            "classTeacher": user_data.classTeacher,
            "tutor": user_data.tutor,
            "olymp": user_data.olymp,
            "noProfOrient": user_data.noProfOrient,
            "etc": user_data.etc,
            "etc2": user_data.etc2,
        }
        for user_data in session.query(create.UserData).filter_by(**params)
    ]

    return users_data

