# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import (index, decode, reports, generateqr_ceibal)

url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET', 'POST'])
url('/api/reports', 'reports', reports, methods=['POST'])
url('/api/getqr', 'generateqr', generateqr_ceibal, methods=['GET', 'POST'])
