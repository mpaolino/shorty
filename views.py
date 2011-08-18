# -*- coding: utf-8 -*-
from . import app
import shorty.libs.shortener as shortener
from shorty.models import (Url, Expansion)
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

    g.decoded_url = Url.query.filter_by(id=decoded_key).first()

    if not g.decoded_url:
        abort(404)

    user_agent = request.user_agent

    from libs.uasparser import UASparser
    uas_parser = UASparser(app.config['UAS_CACHE_DIR'])
    uas_result = uas_parser.parse(user_agent.string)

    new_url_expansion = Expansion(g.decoded_url, user_agent.string,
                                  uas_result['ua_name'],
                                  uas_result['ua_family'],
                                  uas_result['ua_company'],
                                  uas_result['typ'],
                                  uas_result['os_name'],
                                  uas_result['os_family'])

    db_session.add(new_url_expansion)
    db_session.commit()
    return redirect(g.decoded_url.real_url)


def url_register():
    """
    Shorten a new URL
    """
    form = request.form
    if 'url' not in form or 'owner' not in form:
        abort(500)

    reg_url = form['url']
    reg_owner = form['owner']
    #TODO: validate well formed reg_url
    if not reg_url or len(reg_url) <= 1 or not reg_owner\
             or len(reg_owner) <= 1:
        #Invalid URL, redirect to error message
        abort(500)

    already_exists = Url.query.filter_by(real_url=reg_url,
                                         owner_id=reg_owner).first()

    if already_exists:
        return "Already exists: http://ou.vc/%s" % already_exists.encoded_key

    new_url = Url(real_url=reg_url, owner_id=reg_owner)
    db_session.add(new_url)
    # We need to first commit to DB so it's unique integer id is assigned
    db_session.commit()
    # Only then we can ask for the encoded_key, and it will be calculated
    encoded_key = new_url.encoded_key
    db_session.commit()
    return "Success! URL added: http://ou.vc/%s" % encoded_key
