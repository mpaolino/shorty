# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import (index, decode, url_register, reports,
                          generate_qr, get_url)


url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET', 'POST'])
url('/api/<user>/url', 'register', url_register, methods=['POST'])
url('/api/<user>/url/<short>', 'geturl', get_url, methods=['GET', 'POST'])
url('/api/<user>/url/<short>/expansions', 'reports', reports, methods=['GET',
                                                                       'POST'])
url('/api/<user>/url/<short>/qr', 'generateqr', generate_qr,
    methods=['GET', 'POST'])
