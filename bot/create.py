from sqlalchemy import Column, Integer, String, Boolean
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
    # транслит + очистка строки от лишних символов
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

    # динамическая генерация кода для создания n-ного количества столбцов бд
    newColumns = ""
    for gr in groupList:
        newColumns += (gr + " = Column(Boolean)\n")

    exec(newColumns)


print("Запрос...")
google_ss = GoogleSheet()
content = google_ss.read_data_content()
types = google_ss.get_types_of_content()
print("Запрос выполнен")

cols = '\n    '
for i in range(len(types)):

    types[i] = ''.join(c for c in translit(types[i], language_code='ru', reversed=True) if c.isalpha())
    if i == 0:
        add = types[i] + ' = Column(String, primary_key = True)\n    '
    else:
        add = types[i] + ' = Column(String)\n    '

    cols = cols + add

groups = UserData.groupList
# groups = []
# for group in content.keys():
#
#     class_name = ''.join(c for c in translit(group, language_code='ru', reversed=True) if c.isalpha())
#     exec(
#         f"class {class_name}(Base):\n" +
#         f"    __tablename__ = "
#         f"'{''.join(c for c in translit(group, language_code='ru', reversed=True) if c.isalpha()).lower()}_data'" +
#         cols
#     )
#
#     print("Таблица " + class_name + " создана.")
#
#     groups.append(class_name)


class ChatData(Base):

    __tablename__ = 'chat_data'
    chat_id = Column(Integer, primary_key=True)
    start = Column(Boolean)
    name = Column(String)
    register = Column(Boolean)
    group = Column(String)
    status = Column(String)
    class_group = Column(String)


class ContentData(Base):
    __tablename__ = "content_data"
    group = Column(String, primary_key=True)
    for type in types:
        exec(f'{type} = Column(String)\n')


def create():
    # на место postgres:1111 свой логин и пароль
    engine = create_engine("postgresql://postgres:VladMurat228@/postgres")
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
