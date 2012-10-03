# -*- coding: utf-8 -*-
"""
Local settings, instance-specific.
"""
from os.path import abspath, dirname

DEBUG = True

ADMINS = ()
MANAGERS = ADMINS

SECRET_KEY = ''
SERVER_EMAIL = 'root@localhost'

ALLOWED_REFERRERS_REGEXP = r'^http[s]*://[www\.]*ceibal.edu.uy'
