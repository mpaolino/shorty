# -*- coding: utf-8 -*-
from . import app
from shorty.views import *

url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET', 'POST'])
