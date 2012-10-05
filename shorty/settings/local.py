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

RESULTS_PER_PAGE = 500
RESULTS_OUTPUT = 'json'
ALLOWED_REFERRERS_REGEXP = r'^http[s]*://[www\.]*ceibal.edu.uy'
