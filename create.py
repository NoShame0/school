from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import psycopg2

from parse import GoogleSheet

Base = declarative_base()


class UserData(Base):

    __tablename__ = "user_data"
    name = Column(String, primary_key=True)
    #userID = Column(BigInteger)
    parallel = Column(Integer)
    group = Column(String)
    classTeacher = Column(String)
    tutor = Column(String)
    
    olymp = Column(Boolean)
    noProfOrient = Column(Boolean)    
    etc = Column(Boolean)     
    etc2 = Column(Boolean)


def create():
    engine = create_engine("postgresql://postgres:VladMurat228@/postgres")#на место postgres:1111 свой логин и пароль
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database db_school_v2")
    conn.close()


def create_session():
    engine = create_engine("postgresql://postgres:VladMurat228@localhost:5432/db_school_v2")  # сюда тоже
    engine.connect()
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


