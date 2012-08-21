# -*- coding: utf-8 -*-
from shorty import app
from shorty.database import db
from shorty.libs import shortener
from shorty.libs.protobuffer import reports_pb2
from shorty.libs.uasparser import UASparser
from shorty.models import Url, Expansion

from flask import g, abort, redirect, request, send_file, make_response

import re
import calendar


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

    decoded_url = Url.query.filter_by(id=decoded_key).first()

    if not decoded_url:
        abort(404)

    user_agent = request.user_agent

    uas_parser = UASparser(app.config['UAS_CACHE_DIR'])
    uas_result = uas_parser.parse(user_agent.string)

    new_url_expansion = Expansion(decoded_url, user_agent.string,
                                  uas_result['ua_name'],
                                  uas_result['ua_family'],
                                  uas_result['ua_company'],
                                  uas_result['typ'],
                                  uas_result['os_name'],
                                  uas_result['os_family'])

    db.session.add(new_url_expansion)
    db.session.commit()
    return redirect(decoded_url.real_url)


def url_register():
    """
    Shorten a new URL
    """
    form = request.form
    if 'url' not in form or 'owner' not in form:
        abort(501)

    reg_url = form['url']
    reg_owner = form['owner']
    #TODO: validate well formed reg_url
    if not reg_url or len(reg_url) <= 1 or not reg_owner\
             or len(reg_owner) <= 1:
        #Invalid form data, redirect to error message
        abort(501)

    already_exists = Url.query.filter_by(real_url=reg_url,
                                         owner_id=reg_owner).first()

    if already_exists:
        return "Already exists: %s%s" % (request.url_root,
                 already_exists.encoded_key)

    new_url = Url(real_url=reg_url, owner_id=reg_owner)
    db.session.add(new_url)
    # We need to first commit to DB so it's unique integer id is assigned
    # and no race conditions can take place, backend DB atomic operations
    # must assure that
    db.session.commit()
    # Only then we can ask for the encoded_key, and it will be calculated
    encoded_key = new_url.encoded_key
    db.session.commit()
    return "%s%s" % (request.url_root, encoded_key)


def reports():
    """
    Get reports for shorten URL token
    """
    form = request.form
    if 'short_token' not in form or 'owner' not in form:
        abort(501)

    short = form['short_token']
    owner = form['owner']
    page = 1

    if 'page' in form and int(form['page']) >= 0:
        page = form['page']

    if not short or len(short) < 6 or not owner\
             or len(owner) <= 1:
        #Invalid form data, redirect to error message
        abort(501)

    try:
        decoded_key = shortener.decode_url(short)
    except ValueError, e:
        abort(404)

    decoded_url = Url.query.filter_by(id=decoded_key).first()

    if not decoded_url:
        abort(404)

    per_page = app.config['RESULTS_PER_PAGE']
    paginated = Expansion.query.join(Url).filter_by(id=decoded_key)\
                                        .paginate(page=page, per_page=per_page)

    results = reports_pb2.ExpansionsResponse()
    results.short_token = short
    results.owner = owner
    results.page_number = paginated.page
    results.results_per_page = paginated.per_page
    results.page_count = paginated.pages
    encoding = app.config['DEFAULT_CHARSET']
    for result in paginated.items:
        one_result = results.expansion.add()
        one_result.url_id = result.url_id
        detect_unix_ts = calendar.timegm(result.detection_date.utctimetuple())
        one_result.detection_date = detect_unix_ts
        one_result.ua_string = result.ua_string.encode(encoding)
        one_result.ua_name = result.ua_name.encode(encoding)
        one_result.ua_family = result.ua_family.encode(encoding)
        one_result.ua_company = result.ua_company.encode(encoding)
        one_result.ua_type = result.ua_type.encode(encoding)
        one_result.os_family = result.os_family.encode(encoding)

    response = make_response(results.SerializeToString())
    response.headers["Content-type"] = "application/x-protobuffer"
    return response
