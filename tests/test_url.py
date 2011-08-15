import os
from shorty import app
from shorty.database import init_db, db_session
from shorty.models import Url

import unittest2 as unittest
import tempfile


class UrlTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE_URI'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE_URI'])

    def test_url(self):
        url1 = Url(real_url=u'http://cosa.com', owner_id=u'mpaolino')
        db_session.add(url1)
        db_session.commit()
        cacho = url1.encoded_key
        db_session.commit()

if __name__ == '__main__':
    unittest.main()
