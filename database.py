# -*- coding: utf-8 -*-
from shorty import app
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import shorty.models
    db.create_all()
