# -*- coding: utf-8 -*-
from shorty import app
from shorty.database import db
from shorty.libs import shortener
from shorty.libs.protobuffer import reports_pb2
from shorty.libs.uasparser import UASparser
from shorty.models import Url, Expansion
from shorty.validation import (ValidationFailed, validate_url,
                               validate_owner, validate_color,
                               validate_application, validate_application_size,
                               validate_style, validate_qr_format,
                               validate_user, validate_short)
from qrlib import (generate_qr_file, InnerEyeStyleMissing,
                   OuterEyeStyleMissing, StyleMissing)

from flask import (abort, redirect, request, send_file, make_response, jsonify)


@app.errorhandler(ValidationFailed)
def validation_error(val_failed):
    response = jsonify(message='Validation Error', errors=val_failed.errors)
    response.status_code = 422
    return response


def index():
    abort(404)


def decode(encoded):
    """
    Decode URL and redirect
    """
    if not validate_short(encoded):
        abort(404)

    try:
        decoded_key = shortener.decode_url(encoded)
    except ValueError:
        abort(404)

    decoded_url = Url.query.filter_by(id=decoded_key).first_or_404()

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


def url_register(user):
    """
    Shorten a new URL
    """
    values = request.values
    url = values.get('target')
    validation_errors = []

    if not validate_url(url):
        #Invalid form data, redirect to error message
        validation_errors.append({'resource': "url",
                                  'field': "target",
                                  'code': "invalid"})
    if not validate_user(user):
        abort(404)

    if validation_errors:
        raise ValidationFailed(validation_errors)

    already_exists = Url.query.filter_by(real_url=url,
                                         owner_id=user).first()

    if already_exists:
        return jsonify({'url': "%s/%s" % (request.base_url,
                                         already_exists.encoded_key),
                        'target': url,
                        'short': already_exists.encoded_key,
                        'user': user,
                        'creation_date': already_exists.\
                                         date_publish.isoformat(' ')})

    new_url = Url(real_url=url, owner_id=user)
    db.session.add(new_url)
    # We need to first commit to DB so it's unique integer id is assigned
    # and no race conditions can take place, backend DB atomic operations
    # must assure that
    db.session.commit()
    # Only then we can ask for the encoded_key, and it will be calculated
    encoded_key = new_url.encoded_key
    db.session.commit()
    return jsonify({'url': "%s/%s" % (request.base_url, encoded_key),
                    'target': url,
                    'short': encoded_key,
                    'user': user,
                    'creation_date': new_url.date_publish.isoformat(' ')})


def reports(user, short):
    """
    Get reports for shorten URL token
    """
    values = request.values
    page = 1

    if 'page' in values and int(values.get('page')) >= 0:
        page = int(values.get('page'))

    try:
        decoded_key = shortener.decode_url(short)
    except ValueError:
        abort(404)

    decoded_url = Url.query.filter_by(id=decoded_key).first_or_404()

    per_page = app.config['RESULTS_PER_PAGE']
    paginated = Expansion.query.join(Url).filter_by(id=decoded_key)\
                                        .paginate(page=page, per_page=per_page)

    result_output = app.config['RESULTS_OUTPUT']
    if result_output != 'json' and result_output != 'protobuf':
        result_output = 'json'

    if result_output == 'json':
        results = {'short': short, 'user': user,
                   'url': "%s%s" % (request.url_root, short),
                   'target': decoded_url.real_url,
                   'creation_date': decoded_url.date_publish.isoformat(' '),
                   'page_number': paginated.page,
                   'results_per_page': paginated.per_page,
                   'page_count': paginated.pages,
                   'expansions': []}

        for result in paginated.items:
            one_result = {'detection_date': result.detection_date.\
                                                                isoformat(' '),
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
        results.short = short
        results.user = user
        results.target = decoded_url.real_url
        results.page_number = paginated.page
        results.results_per_page = paginated.per_page
        results.page_count = paginated.pages
        encoding = app.config['DEFAULT_CHARSET']

        for result in paginated.items:
            one_result = results.expansion.add()
            one_result.detection_date = result.detection_date.\
                                                              isoformat(' ')
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


def generate_qr(user, short):
    """
    Return QR for given URL
    """
    values = request.values
    validation_errors = []

    try:
        decoded_id = shortener.decode_url(short)
    except ValueError:
        abort(404)

    if not validate_owner(user):
        validation_errors.append({'resource': "user",
                                  'field': "id",
                                  'code': "invalid"})

    Url.query.filter_by(id=decoded_id, owner_id=user).first_or_404()

    def get_optional(name, default, validator):
        value = values.get(name)
        if value == None:
            return default
        if callable(validator) and not validator(value):
            validation_errors.append({'resource': "qr",
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
    qr_format = get_optional('qrformat', 'PDF', validate_qr_format)

    if validation_errors:
        raise ValidationFailed(validation_errors)

    pdf_filelike = None
    try:
        pdf_filelike = generate_qr_file("%s%s" % (request.url_root,
                                        short),
                                        app=application,
                                        app_size=appsize,
                                        style=style,
                                        style_color=style_color,
                                        inner_eye_style=inner_eye_style,
                                        inner_eye_color=inner_eye_color,
                                        outer_eye_style=outer_eye_style,
                                        outer_eye_color=outer_eye_color,
                                        bg_color=bg_color,
                                        qr_format=qr_format)

        pdf_filelike.seek(0)
    except InnerEyeStyleMissing:
        validation_errors.append({'resource': "url",
                                  'field': 'innereyestyle',
                                  'code': "invalid"})
        raise ValidationFailed(validation_errors)
    except OuterEyeStyleMissing:
        validation_errors.append({'resource': "url",
                                  'field': 'outereyestyle',
                                  'code': "invalid"})
        raise ValidationFailed(validation_errors)
    except StyleMissing:
        validation_errors.append({'resource': "url",
                                  'field': 'style',
                                  'code': "invalid"})
        raise ValidationFailed(validation_errors)
    except Exception, e:
        print e
        abort(500)
    else:
        qr_format = qr_format.upper()
        if qr_format == 'PDF':
            mimetype = u'application/pdf'
        elif qr_format == 'PNG':
            mimetype = u'image/png'
        elif qr_format == 'GIF':
            mimetype = u'image/gif'
        elif qr_format == 'JPEG':
            mimetype = u'image/jpeg'

        return send_file(pdf_filelike, mimetype=mimetype)


def get_url(user, short):
    """Returns URL details for given short token"""
    try:
        decoded_id = shortener.decode_url(short)
    except ValueError:
        abort(404)

    url = Url.query.filter_by(id=decoded_id, owner_id=user).first_or_404()

    return jsonify({'target': url.real_url,
                    'short': short,
                    'user': user,
                    'creation_date': url.date_publish.isoformat(' '),
                    'url': request.base_url})


def get_all_urls(user):
    """Returns all URLs defined for user"""

    Url.query.filter_by(owner_id=user).first_or_404()

    values = request.values
    page = 1

    if 'page' in values and int(values.get('page')) >= 0:
        page = int(values.get('page'))

    per_page = app.config['RESULTS_PER_PAGE']
    paginated = Url.query.filter_by(owner_id=user).paginate(page=page,
                                                            per_page=per_page)

    result_output = app.config['RESULTS_OUTPUT']
    if result_output != 'json' and result_output != 'protobuf':
        result_output = 'json'

    if result_output == 'json':
        results = {'user': user,
                   'page_number': paginated.page,
                   'results_per_page': paginated.per_page,
                   'page_count': paginated.pages,
                   'urls': []}

        for url in paginated.items:
            one_result = {'target': url.real_url,
                          'short': url.encoded_key,
                          'creation_date': url.date_publish.isoformat(' '),
                          'url': "%s/%s" % (request.base_url, url.encoded_key)}
            results['urls'].append(one_result)
        return jsonify(results)
