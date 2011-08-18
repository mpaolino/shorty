import os
from shorty import app
from shorty.models import Url
from shorty.database import init_db, db_session

import unittest2 as unittest
import pdb


class UrlTestCase(unittest.TestCase):

    def setUp(self):
        init_db()

    def tearDown(self):
        os.close(app.config['DB_FD'])
        os.unlink(app.config['DATABASE'])

    def test_url(self):
        url1 = Url(real_url=u'http://cosa.com', owner_id=u'mpaolino')
        db_session.add(url1)
        db_session.commit()
        cacho = url1.encoded_key
        db_session.commit()
        url2 = Url(real_url=u'http://cosa.com', owner_id=u'mpaolino')
