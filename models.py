from enum import auto
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'bot_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer)
    country = Column(String)
    city = Column(String)

    def __repr__(self):
        info = {
            'tel_id': self.telegram_id,
            'country': self.country,
            'city': self.city
        }

        return info