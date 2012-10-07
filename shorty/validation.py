# -*- coding: utf-8 -*-
import re
import iso8601
from iso8601 import ParseError


class ValidationFailed(Exception):

    def __init__(self, errors):
        self.message = "Validation Failed"
        self.errors = errors

    def __str__(self):
        return "ValidationError"


def validate_user(user):
    if isinstance(user, (str, unicode)) and \
            re.match('^[a-z,A-Z,0-9]{1,10}$', user):
        return True
    return False


def validate_date(date):
    try:
        iso8601.parse_date(date)
        return True
    except ParseError:
        return False


def validate_url(url):
    #TODO: proper URL validation
    if isinstance(url, (str, unicode)) and len(url) > 5:
        return True
    return False


def validate_short(short):
    if isinstance(short, (str, unicode)) and re.match("^[a-zA-Z0-9]+", short):
        return True
    return False


def validate_owner(owner):
    if isinstance(owner, (str, unicode)) and len(owner) >= 1:
        return True
    return False


def validate_style(style):
    if isinstance(style, (str, unicode)) and len(style) >= 1:
        return True
    return False


def validate_application_size(appsize):
    if isinstance(appsize, (unicode, str)):
        appsize = appsize.lower()
    else:
        return False
    all_sizes = set(['large', 'medium', 'small'])
    if appsize in all_sizes:
        return True
    return False


def validate_application(application):
    if isinstance(application, (unicode, str)):
        application = application.lower()
    else:
        return False
    if application in set(['interior', 'exterior']):
        return True
    return False


def validate_qr_format(qr_format):
    if isinstance(qr_format, (unicode, str)):
        qr_format = qr_format.upper()
    else:
        return False
    if qr_format in set(['PDF', 'PNG', 'GIF', 'JPEG']):
        return True
    return False


def validate_color(color):
    if not isinstance(color, (unicode, str)):
        return False
    if re.match('\#[0-9A-Fa-f]{6}', color):
        return True
    return False
