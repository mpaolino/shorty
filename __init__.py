# -*- coding: utf-8 -*-
from flask import Flask
import logging
import sys

__authors__ = (u'Alvaro Mouriño <alvaro@ideal.com.uy>',
               u'Miguel Paolino <miguel@ideal.com.uy>')
__version__ = '0.0.1'
__flask_version__ = '0.7.2'

try:
    from shorty import settings
except ImportError:
    logging.error('Could not find settings. Aborting...')
    sys.exit(1)

app = Flask(__name__)
app.config.from_object(settings)

from shorty.routes import *

if __name__ == '__main__':
    app.run(debug=True)
