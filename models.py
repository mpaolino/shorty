# -*- coding: utf-8 -*-
from shorty.database import Base
from shorty.libs.shortener import UrlEncoder

from sqlalchemy import (Column, Integer, UnicodeText, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime


class Url(Base):

    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
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
        self._encoded_key = encoder.encode_url(self.id)
        return self._encoded_key


class Expansion(Base):

    __tablename__ = 'expansions'

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'))
    url = relationship(Url, primaryjoin=url_id == Url.id)
    detection_date = Column(DateTime, nullable=False, default=datetime.now())
    ua_string = Column(UnicodeText, unique=False, nullable=True)
    ua_name = Column(UnicodeText, unique=False, nullable=True)
    ua_family = Column(UnicodeText, unique=False, nullable=True)
    ua_company = Column(UnicodeText, unique=False, nullable=True)
    ua_type = Column(UnicodeText, unique=False, nullable=True)
    os_family = Column(UnicodeText, unique=False, nullable=True)

    def __init__(self, url, ua_string, ua_name, ua_family, ua_company, ua_type,
                    os_name, os_family):
        self.url = url
        self.ua_string = ua_string
        self.ua_name = ua_name
        self.ua_family = ua_family
        self.ua_company = ua_company
        self.ua_type = ua_type
        self.os_name = os_name
        self.os_family = os_family
        self.detection_date = datetime.now()
