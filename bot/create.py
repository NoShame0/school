from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import psycopg2

from transliterate import translit

from parse import GoogleSheet

Base = declarative_base()


class UserData(Base):

    googleSheet = GoogleSheet()
    ruGroupList = googleSheet.get_groups_of_students()
    groupList = []
    #транслит + очистка строки от лишних символов
    for gr in ruGroupList:
        translitGr = translit(gr, language_code='ru', reversed=True)
        clearGr = "".join(c for c in translitGr if c.isalpha())
        groupList.append(clearGr)

    __tablename__ = "user_data"
    name = Column(String, primary_key=True)
    parallel = Column(Integer)
    group = Column(String)
    classTeacher = Column(String)
    tutor = Column(String)

    #динамическая генерация кода для создания n-ного количества столбцов бд
    newColumns = ""
    for gr in groupList:
        newColumns += (gr + " = Column(Boolean)\n")

    exec(newColumns)


def create():
    engine = create_engine("postgresql://postgres:VladMurat228@/postgres")#на место postgres:1111 свой логин и пароль
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database db_school_v21")
    conn.close()


def create_session():
    engine = create_engine("postgresql://postgres:VladMurat228@localhost:5432/db_school_v21")  # сюда тоже
    engine.connect()
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


