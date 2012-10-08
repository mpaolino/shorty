# -*- coding: utf-8 -*-
# Copyright (C) 2012, Miguel Paolino <mpaolino@ideal.com.uy>
from shorty.database import db
from shorty.libs.shortener import UrlEncoder

from datetime import datetime


class Url(db.Model):

    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    real_url = db.Column(db.UnicodeText, unique=False, nullable=False)
    _encoded_key = db.Column(db.String(6), unique=True, nullable=True)
    date_publish = db.Column(db.DateTime, nullable=False,
                             default=datetime.now())
    owner_id = db.Column(db.UnicodeText, unique=False, nullable=False)

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


class Expansion(db.Model):

    __tablename__ = 'expansions'

    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'))
    url = db.relationship(Url, backref=db.backref('expansions',
                                                  lazy='dynamic'))
    detection_date = db.Column(db.DateTime, nullable=False,
                               default=datetime.now())
    ua_string = db.Column(db.UnicodeText, unique=False, nullable=True)
    ua_name = db.Column(db.UnicodeText, unique=False, nullable=True)
    ua_family = db.Column(db.UnicodeText, unique=False, nullable=True)
    ua_company = db.Column(db.UnicodeText, unique=False, nullable=True)
    ua_type = db.Column(db.UnicodeText, unique=False, nullable=True)
    os_family = db.Column(db.UnicodeText, unique=False, nullable=True)

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
