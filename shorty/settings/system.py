# -*- coding: utf-8 -*-
"""
System-wide settings.
"""
from gettext import gettext as _
from os.path import abspath, dirname, join

PROJECT_DIR = dirname(abspath(__file__))[:-len('/settings')]
DATABASE_URI = 'sqlite:///%s/shorty.db' % (PROJECT_DIR)
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_ECHO = False

DEBUG = False

CSRF_ENABLED = True
DEFAULT_CHARSET = 'utf-8'

UAS_CACHE_DIR = '%s/libs/uas_cache' % (PROJECT_DIR)
RESULTS_PER_PAGE = 5000
