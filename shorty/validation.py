# -*- coding: utf-8 -*-
import re


class ValidationFailed(Exception):

    def __init__(self, errors):
        self.message = "Validation Failed"
        self.errors = errors

    def __str__(self):
        return "ValidationError"


def validate_url(url):
    if isinstance(url, (str, unicode)) and len(url) > 4:
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
    all_sizes = ['large', 'medium', 'small']
    if appsize in all_sizes:
        return True
    return False


def validate_application(application):
    if isinstance(application, (unicode, str)):
        application = application.lower()
    else:
        return False
    if application in ('interior', 'exterior'):
        return True
    return False


def validate_color(color):
    if not isinstance(color, (unicode, str)):
        return False
    if re.match('\#[0-9A-Fa-f]{6}', color):
        return True
    return False
