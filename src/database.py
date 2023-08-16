from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# 接続先DBの設定
DATABASE = 'sqlite:///reserve_classroom.sqlite3'

# Engineの作成
Engine = create_engine(
    DATABASE,
    echo=False,
    connect_args={"check_same_thread": False}
)


Base = declarative_base()


class Classroom(Base):

    __tablename__ = 'classroom'

    classroom_id = Column(Integer,primary_key=True)
    classroom_name = Column(String)
    
    def to_dict(self):
        classroom = {
            "classroom_id": self.classroom_id,
            "classroom_name": self.classroom_name
        }
        
        return classroom


class Reservation(Base):

    __tablename__ = 'reservation'

    reservation_id = Column(String,primary_key=True)
    classroom_id = Column(Integer)
    # user_id = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    def to_dict(self):
        reservation = {
            "reservation_id":self.reservation_id,
            "classroom_id":self.classroom_id,
            # "user_id":self.user_id,
            "start_time":self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time":self.end_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        return reservation


class User(Base):

    __tablename__ = 'user'
    
    user_id = Column(Integer,primary_key=True)
    user_name = Column(String)
    user_email = Column(String)
    
    def to_dict(self):
        user = {
            "user_id":self.user_id,
            "user_name":self.user_name,
            "user_email":self.user_email
        }

        return user


def create_database():
    Base.metadata.create_all(bind=Engine)


def create_session():
    return sessionmaker(bind=Engine)()