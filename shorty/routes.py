# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import index, decode, url_register, reports

url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET', 'POST'])
url('/register', 'register', url_register, methods=['POST'])
url('/reports', 'reports', reports, methods=['POST'])
