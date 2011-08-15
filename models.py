# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, UnicodeText, DateTime
from shorty.database import Base
from shorty.libs.shortener import UrlEncoder
from datetime import datetime


class Url(Base):

    __tablename__ = 'urls'

    url_id = Column(Integer, primary_key=True, autoincrement=True)
    real_url = Column(UnicodeText, unique=False, nullable=False)
    _encoded_key = Column(UnicodeText, unique=True, nullable=True)
    date_publish = Column(DateTime, nullable=False, default=datetime.now())
    owner_id = Column(UnicodeText, unique=False, nullable=False)

    def __init__(self, real_url, owner_id):
        self.real_url = real_url
        self.owner_id = owner_id
        self.date_publish = datetime.now()

    @property
    def encoded_key(self):
        if self._encoded_key:
            return self._encoded_key
        encoder = UrlEncoder()
        self._encoded_key = encoder.encode_url(self.url_id)
        return self._encoded_key
