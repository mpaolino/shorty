# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import (index, decode, url_register, reports,
                          generateqr)

url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET', 'POST'])
url('/api/register', 'register', url_register, methods=['POST'])
url('/api/reports', 'reports', reports, methods=['POST'])
url('/api/getqr', 'generateqr', generateqr, methods=['GET', 'POST'])
