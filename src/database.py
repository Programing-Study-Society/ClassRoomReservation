from sqlalchemy import create_engine, Column, String, DateTime, Boolean
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
            "reservable-start-date": self.reservable_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "reservable-end-date": self.reservable_end_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return classroom


class Reservation(Base):

    __tablename__ = 'reservation'

    reservation_id = Column('reservation_id', String,primary_key=True)
    classroom_id = Column('reserved_classroom_id', String)
    reserved_user_id = Column('reserved_user_id', String(64))
    start_time = Column('start_date', DateTime)
    end_time = Column('end_date', DateTime)

    def to_dict(self, is_required_user_id=False):

        session = create_session()

        classroom = session.query(ReservableClassroom)\
            .filter(
                ReservableClassroom.classroom_id == self.classroom_id
            ).first()

        reservation = {
            "reservation-id":self.reservation_id,
            "classroom-name":classroom.classroom_name,
            "start-date":self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end-date":self.end_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # must change
        if is_required_user_id == True :
            user = session.query(User).filter(User.user_id == self.reserved_user_id).first()
            if user != None :
                reservation['user-name'] = user.user_name
                reservation['user-email'] = user.user_email

        return reservation
    

class User(UserMixin, Base):
    
    __tablename__ = 'user'
    
    user_id = Column('user_id', String(64), primary_key=True)
    user_email = Column('user_email', String)
    user_name = Column('user_name',String(128))
    user_state = Column('user_state', String)
    user_sub = Column('user_sub', String, nullable=True)

    def get_id(self):
        return self.user_id
    
    # must change
    def to_dict(self):
        user = {
            "approved-user-id":self.user_id,
            "approved-user-name":self.user_name,
            "approved-email":self.user_email,
            "user-state":self.user_state,
            "approved-user-sub":self.user_sub
        }

        return user
    

class Authority(Base):

    __tablename__ = 'authority'

    name = Column('user_state_name', String, primary_key=True)
    is_reserve = Column('is_reserve', Boolean)
    is_admin = Column('is_admin', Boolean)
    is_edit_reserve = Column('is_edit_reserve', Boolean)
    is_edit_user = Column('is_edit_user', Boolean)

    def to_dict(self) :
        authority = {
            'name':self.name,
            'is-reserve':self.is_reserve,
            'is-admin':self.is_admin,
            'is-edit-reserve':self.is_edit_reserve,
            'is-edit-user':self.is_edit_user
        }

        return authority



def create_database():
    Base.metadata.create_all(bind=Engine)


def create_session():
    return sessionmaker(bind=Engine, expire_on_commit=False)()


def create_scoped_session():
    return scoped_session(sessionmaker(bind=Engine))()