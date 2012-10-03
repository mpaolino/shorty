# -*- coding: utf-8 -*-
from shorty import app
from shorty.database import db
from shorty.libs import shortener
from shorty.libs.protobuffer import reports_pb2
from shorty.libs.uasparser import UASparser
from shorty.models import Url, Expansion
from shorty.validation import (ValidationFailed, validate_url_ceibal, 
                               validate_url, validate_owner, validate_color,
                               validate_application, validate_application_size,
                               validate_style)

from qrlib import generate_qr_file

from flask import (abort, redirect, request, send_file, make_response, jsonify)

import re
import calendar
import ipdb


@app.errorhandler(404)
def page_not_found(error):
    return 'Sorry, wrong URL', 404


@app.errorhandler(ValidationFailed)
def validation_error(val_failed):
    return (jsonify(message='Validation Error',
                    errors=val_failed.errors),
            422)


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
    except ValueError:
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
    mandatory_params = ['short_token', 'owner']

    if False in map(lambda x: x in form, mandatory_params):
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
    except ValueError:
        abort(404)

    decoded_url = Url.query.filter_by(id=decoded_key).first()

    if not decoded_url:
        abort(404)

    per_page = app.config['RESULTS_PER_PAGE']
    paginated = Expansion.query.join(Url).filter_by(id=decoded_key)\
                                        .paginate(page=page, per_page=per_page)

    result_output = app.config['RESULTS_OUTPUT']
    if result_output != 'json' or result_output != 'protobuf':
        result_output = 'json'

    if result_output == 'json':
        results = {'short_url': short, 'owner': owner,
                   'page_number': paginated.page,
                   'results_per_page': paginated.per_page,
                   'page_count': paginated.pages,
                   'expansions': []}

        for result in paginated.items:
            detect_unix_ts = calendar.timegm(
                                         result.detection_date.utctimetuple())
            one_result = {'url_id': result.url_id,
                          'detection_date': detect_unix_ts,
                          'ua_string': result.ua_string,
                          'ua_name': result.ua_name,
                          'ua_family': result.ua_family,
                          'ua_company': result.ua_company,
                          'ua_type': result.ua_type,
                          'os_family': result.os_family}

            results['expansions'].append(one_result)
        return jsonify(results)

    if result_output == 'protobuf':
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
            detect_unix_ts = calendar.timegm(
                                         result.detection_date.utctimetuple())
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

    abort(500)


def generateqr_ceibal():
    """
    Return QR for given URL
    """
    values = request.values
    validation_errors = []

    url = request.referrer
    if url:
        if not validate_url_ceibal(url):
            validation_errors.append({'resource': "url",
                                      'field': "url",
                                      'code': "invalid"})
    else:
        validation_errors.append({'resource': "url",
                                  'field': "url",
                                  'code': "missing_field"})

    owner = 'ceibal'

    def get_optional(name, default, validator):
        value = values.get(name)
        if value == None:
            return default
        if callable(validator) and not validator(value):
            validation_errors.append({'resource': "url",
                                      'field': name,
                                      'code': "invalid"})
            return default
        return value

    application = get_optional('application', 'interior', validate_application)
    appsize = get_optional('appsize', 'small', validate_application_size)
    style = get_optional('style', 'default', validate_style)
    style_color = get_optional('stylecolor', '#195805', validate_color)
    inner_eye_style = get_optional('innereyestyle', 'default', validate_style)
    outer_eye_style = get_optional('outereyestyle', 'default', validate_style)
    inner_eye_color = get_optional('innereyecolor', '#C21217', validate_color)
    outer_eye_color = get_optional('outereyecolor', '#22C13E', validate_color)
    bg_color = get_optional('bgcolor', '#FFFFFF', validate_color)

    if validation_errors:
        raise ValidationFailed(validation_errors)

    already_exists = Url.query.filter_by(real_url=url,
                                         owner_id=owner).first()
    encoded_key = None
    if already_exists:
        encoded_key = already_exists.encoded_key
    else:
        new_url = Url(real_url=url, owner_id=owner)
        db.session.add(new_url)
        # We need to first commit to DB so it's unique integer id is assigned
        # and no race conditions can take place, backend DB atomic operations
        # must assure that
        db.session.commit()
        # Only then we can ask for the encoded_key, and it will be calculated
        encoded_key = new_url.encoded_key
        db.session.commit()

    pdf_filelike = None
    try:
        pdf_filelike = generate_qr_file("%s%s" % (request.url_root,
                                        encoded_key),
                                        app=application,
                                        app_size=appsize,
                                        style=style,
                                        style_color=style_color,
                                        inner_eye_style=inner_eye_style,
                                        inner_eye_color=inner_eye_color,
                                        outer_eye_style=outer_eye_style,
                                        outer_eye_color=outer_eye_color,
                                        bg_color=bg_color,
                                        qr_format='PDF')

        pdf_filelike.seek(0)
    except Exception, e:
        print e
        abort(500)
    else:
        return send_file(pdf_filelike, mimetype=u'application/pdf')


def generateqr():
    """
    Return QR for given URL
    """
    values = request.values
    validation_errors = []

    url = values.get('url')
    if url:
        if not validate_url(url):
            validation_errors.append({'resource': "url",
                                      'field': "url",
                                      'code': "invalid"})
    else:
        validation_errors.append({'resource': "url",
                                  'field': "url",
                                  'code': "missing_field"})

    owner = values.get('owner')
    if owner:
        owner = owner.lower()
        if not validate_owner(owner):
            validation_errors.append({'resource': "url",
                                     'field': "owner",
                                     'code': "invalid"})
    else:
        validation_errors.append({'resource': "url",
                                  'field': "owner",
                                  'code': "missing_field"})

    def get_optional(name, default, validator):
        value = values.get(name)
        if value == None:
            return default
        if callable(validator) and not validator(value):
            validation_errors.append({'resource': "url",
                                      'field': name,
                                      'code': "invalid"})
            return default
        return value

    application = get_optional('application', 'interior', validate_application)
    appsize = get_optional('appsize', 'small', validate_application_size)
    style = get_optional('style', 'default', validate_style)
    style_color = get_optional('stylecolor', '#000000', validate_color)
    inner_eye_style = get_optional('innereyestyle', 'default', validate_style)
    outer_eye_style = get_optional('outereyestyle', 'default', validate_style)
    inner_eye_color = get_optional('innereyecolor', '#000000', validate_color)
    outer_eye_color = get_optional('outereyecolor', '#000000', validate_color)
    bg_color = get_optional('bgcolor', '#FFFFFF', validate_color)

    if validation_errors:
        raise ValidationFailed(validation_errors)

    already_exists = Url.query.filter_by(real_url=url,
                                         owner_id=owner).first()
    encoded_key = None
    if already_exists:
        encoded_key = already_exists.encoded_key
    else:
        new_url = Url(real_url=url, owner_id=owner)
        db.session.add(new_url)
        # We need to first commit to DB so it's unique integer id is assigned
        # and no race conditions can take place, backend DB atomic operations
        # must assure that
        db.session.commit()
        # Only then we can ask for the encoded_key, and it will be calculated
        encoded_key = new_url.encoded_key
        db.session.commit()

    pdf_filelike = None
    try:
        pdf_filelike = generate_qr_file("%s%s" % (request.url_root,
                                        encoded_key),
                                        app=application,
                                        app_size=appsize,
                                        style=style,
                                        style_color=style_color,
                                        inner_eye_style=inner_eye_style,
                                        inner_eye_color=inner_eye_color,
                                        outer_eye_style=outer_eye_style,
                                        outer_eye_color=outer_eye_color,
                                        bg_color=bg_color,
                                        qr_format='PDF')

        pdf_filelike.seek(0)
    except Exception, e:
        print e
        abort(500)
    else:
        return send_file(pdf_filelike, mimetype=u'application/pdf')
