from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from flask_login import UserMixin

# 接続先DBの設定
DATABASE = 'sqlite:///reserve_classroom.sqlite3'

# Engineの作成
Engine = create_engine(
    DATABASE,
    echo=False,
    connect_args={"check_same_thread": False}
)


Base = declarative_base()


class ReservableClassroom(Base):

    __tablename__ = 'reservable_classroom'

    classroom_id = Column('classroom_id', String, primary_key=True)
    classroom_name = Column('classroom_name', String)
    reservable_start_time = Column('reservable_start_date', DateTime)
    reservable_end_time = Column('reservable_end_date', DateTime)
    
    def to_dict(self):
        classroom = {
            "classroom-id": self.classroom_id,
            "classroom-name": self.classroom_name,
            "reservable-start-date": self.reservable_start_time,
            "reservable-end-date": self.reservable_end_time
        }
        
        return classroom


class Reservation(Base):

    __tablename__ = 'reservation'

    reservation_id = Column('reservation_id', String,primary_key=True)
    classroom_id = Column('reserved_classroom_id', Integer)
    reserved_user_id = Column('reserved_user_id', Integer)
    start_time = Column('start_date', DateTime)
    end_time = Column('end_date', DateTime)

    def to_dict(self, is_required_user_id=False):

        session = create_session()

        classroom = session.query(ReservableClassroom.classroom_name)\
            .filter(
                ReservableClassroom.classroom_id == self.classroom_id
            ).first()

        reservation = {
            "reservation-id":self.reservation_id,
            "classroom-name":classroom.classroom_name,
            "start-date":self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end-date":self.end_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if is_required_user_id :
            user = session.query(User).filter(User.user_id == self.reserved_user_id).first()

            if user != None :
                reservation['user-name'] = user.user_name
                reservation['user-email'] = user.user_email

        return reservation


class User(UserMixin, Base):

    __tablename__ = 'user'
    
    user_id = Column('user_id',String(64),primary_key=True)
    user_name = Column('user_name',String(128))
    user_email = Column('user_email', String)

    def get_id(self):
        return self.user_id
    
    def to_dict(self):
        user = {
            "user-id":self.user_id,
            "user-name":self.user_name,
            "user-email":self.user_email
        }

        return user
    

class Approved_User(Base):
    
    __tablename__ = 'approved_user'
    
    approved_email = Column('approved_email', String, primary_key=True)
    approved_user_name = Column('approved_user_name',String(128))
    is_admin = Column('is_admin', Boolean)
    
    def to_dict(self):
        approved_user = {
            "approved-user-name":self.approved_user_name,
            "approved-email":self.approved_email,
            "is-admin":self.is_admin,
        }

        return approved_user


def create_database():
    Base.metadata.create_all(bind=Engine)


def create_session():
    return sessionmaker(bind=Engine, expire_on_commit=False)()


def create_scoped_session():
    return scoped_session(sessionmaker(bind=Engine))()