# -*- coding: utf-8 -*-
from . import app
import shorty.libs.shortener as shortener
from shorty.models import Url
from shorty.database import db_session
from flask import (g, abort, redirect, request)

import re
import pdb


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@app.errorhandler(404)
def page_not_found(error):
    return 'Wrong URL', 404


def index():
    abort(404)


def decode(encoded):
    """
    Decode URL and redirect
    """
    if not encoded or len(encoded) <= 1 or not \
            re.match("^[a-zA-Z0-9]+", encoded):
        abort(404)

    try:
        decoded_key = shortener.decode_url(encoded)
    except ValueError, e:
        abort(404)

    g.decoded_url = Url.query.filter(Url.url_id == decoded_key).first()

    if not g.decoded_url:
        abort(404)
    return redirect(g.decoded_url.real_url)


def url_register(real_url):
    """
    Shorten a new URL
    """
    #TODO: validate real_url
    if not real_url or len(real_url) <= 1:
        #Invalid URL, redirect to error message
        abort(404)

    already_exists = Url.query.filter(Url.real_url == real_url)

    if already_exists:
        return "Duplicated: http://ou.vc/%s" % already_exists.encoded_key

    g.last_shortened = Url.query.order_by(desc(Url.url_id)).limit(1)
    if not g.last_shortened:
        abort(404)
    shorten_url = g.last_shortened.encoded_key
    db_session.commit()
    return "Success! URL added: http://ou.vc/%s" % shorten_url
