# -*- coding: utf-8 -*-
from shorty import app
from shorty.views import (index, decode, reports, generate_qr_ceibal,
                          get_url, get_all_urls, delete_url)


url = app.add_url_rule

url('/', 'index', index)
url('/<encoded>', 'decode', decode, methods=['GET'])
url('/api/url', 'getallurls', get_all_urls, methods=['GET'])
url('/api/url/<short>', 'geturl', get_url, methods=['GET'])
url('/api/url/<short>', 'deleteurl', delete_url, methods=['DELETE'])
url('/api/url/<short>/expansions', 'reports', reports, methods=['GET', 'POST'])
url('/api/qr', 'generateqr', generate_qr_ceibal, methods=['GET', 'POST'])
