# *- coding: utf-8 -*-
from shorty import app
from shorty.database import db
from shorty.libs import shortener
from shorty.libs.uasparser import UASparser
from shorty.models import Url, Expansion
from shorty.validation import (ValidationFailed, validate_url_ceibal,
                               validate_color, validate_application,
                               validate_style, validate_qr_format,
                               validate_short, validate_date,
                               validate_application_size)

from qrlib import (generate_qr_file, InnerEyeStyleMissing,
                   OuterEyeStyleMissing, StyleMissing)

from flask import (abort, redirect, request, send_file, make_response, jsonify)
import iso8601


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


def reports(short):
    """
    Get reports for shorten URL token
    """
    user = 'ceibal'
    values = request.values
    page = 1
    validation_errors = []

    if 'page' in values and int(values.get('page')) >= 0:
        page = int(values.get('page'))

    try:
        decoded_key = shortener.decode_url(short)
    except ValueError:
        abort(404)

    decoded_url = Url.query.filter_by(id=decoded_key).first_or_404()

    def get_optional(name, default, validator):
        value = values.get(name)
        if value == None:
            return default
        if callable(validator) and not validator(value):
            validation_errors.append({'resource': "reports",
                                      'field': name,
                                      'code': "invalid"})
            return default
        return value

    from_string = get_optional('from', None, validate_date)
    to_string = get_optional('to', None, validate_date)

    if (from_string and to_string) and (to_string < from_string):
        validation_errors.append({'resource': "reports",
                                  'field': 'from',
                                  'code': "invalid",
                                  'details': 'to date prior to from date'})
        raise ValidationFailed(validation_errors)

    per_page = app.config['RESULTS_PER_PAGE']
    # Let's see what are the query conditionals
    if from_string and not to_string:
        from_date = iso8601.parse_date(from_string)
        paginated = Expansion.query.join(Url)\
                    .filter((Url.id == decoded_key) &\
                            (Expansion.detection_date >= from_date))\
                    .paginate(page=page, per_page=per_page)

    elif not from_string and to_string:
        to_date = iso8601.parse_date(to_string)
        paginated = Expansion.query.join(Url)\
                    .filter((Url.id == decoded_key) &\
                            (Expansion.detection_date <= to_date))\
                    .paginate(page=page, per_page=per_page)

    elif from_string and to_string:
        from_date = iso8601.parse_date(from_string)
        to_date = iso8601.parse_date(to_string)
        paginated = Expansion.query.join(Url)\
                    .filter((Url.id == decoded_key) &\
                            (Expansion.detection_date <= to_date) &\
                            (Expansion.detection_date >= from_date))\
                    .paginate(page=page, per_page=per_page)
    else:
        paginated = Expansion.query.join(Url).filter_by(id=decoded_key)\
                                        .paginate(page=page, per_page=per_page)

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


def get_url(short):
    """Returns URL details for given short token"""

    user = 'ceibal'

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


def delete_url(short):
    """Deletes URL for given user and short token"""

    user = 'ceibal'

    try:
        decoded_id = shortener.decode_url(short)
    except ValueError:
        abort(404)
    url = Url.query.filter_by(id=decoded_id, owner_id=user).first_or_404()
    db.session.delete(url)
    db.session.commit()
    response = make_response()
    response.status_code = 204
    return response


def get_all_urls():
    """Returns all URLs defined for user"""

    user = 'ceibal'

    Url.query.filter_by(owner_id=user).first_or_404()

    values = request.values
    page = 1

    if 'page' in values and int(values.get('page')) >= 0:
        page = int(values.get('page'))

    per_page = app.config['RESULTS_PER_PAGE']
    paginated = Url.query.filter_by(owner_id=user).paginate(page=page,
                                                            per_page=per_page)

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


def generate_qr_ceibal():
    """
    Return QR for given URL
    """
    values = request.values
    validation_errors = []

    url = request.referrer
    if not url or not validate_url_ceibal(url):
        abort(403)

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
    style = get_optional('style', 'heavyround', validate_style)
    style_color = get_optional('stylecolor', '#195805', validate_color)
    inner_eye_style = get_optional('innereyestyle', 'heavyround',
                                   validate_style)
    outer_eye_style = get_optional('outereyestyle', 'heavyround',
                                   validate_style)
    inner_eye_color = get_optional('innereyecolor', '#C21217', validate_color)
    outer_eye_color = get_optional('outereyecolor', '#22C13E', validate_color)
    bg_color = get_optional('bgcolor', '#FFFFFF', validate_color)
    qr_format = get_optional('qrformat', 'PDF', validate_qr_format)

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
