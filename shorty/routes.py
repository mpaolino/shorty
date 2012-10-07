# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import (index, decode, url_register, reports,
                          generate_qr, get_url, get_all_urls,
                          delete_url)


url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET'])
url('/api/<user>/url', 'register', url_register, methods=['POST'])
url('/api/<user>/url', 'getallurls', get_all_urls, methods=['GET'])
url('/api/<user>/url/<short>', 'geturl', get_url, methods=['GET'])
url('/api/<user>/url/<short>', 'deleteurl', delete_url, methods=['DELETE'])
url('/api/<user>/url/<short>/expansions', 'reports', reports, methods=['GET',
                                                                       'POST'])
url('/api/<user>/url/<short>/qr', 'generateqr', generate_qr,
    methods=['GET', 'POST'])
