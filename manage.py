# -*- coding: utf-8 -*-
from os.path import abspath, dirname
import tempfile
import sys


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: Not enough arguments.')
        sys.exit(1)

    if sys.argv[1] == 'shell':
        import IPython
        from models import *

        mktestbed()
        IPython.Shell.start().mainloop()
    elif sys.argv[1] == 'runserver':
        from shorty import app
        try:
            from shorty import settings
        except ImportError:
            logging.error('Could not find settings. Aborting...')
            sys.exit(1)

        app.config.from_object(settings)

        from shorty.routes import *
        from shorty.database import init_db
        init_db()
        app.run(debug=True)
    elif sys.argv[1] == 'test':
        from shorty import app
        import unittest2 as unittest
        import logging
        import sys
    
        db_fd, tmp_file = tempfile.mkstemp()
        full_db_uri = 'sqlite:///%s' % tmp_file
        app.config['DATABASE'] = tmp_file
        app.config['DB_FD'] = db_fd
        app.config['DATABASE_URI'] = full_db_uri
        app.config['SQLALCHEMY_DATABASE_URI'] = full_db_uri 
        app.config['TESTING'] = True
 
        path = sys.argv[2] if len(sys.argv) == 3 else './tests'
        suite = unittest.loader.TestLoader().discover(path)
        unittest.TextTestRunner(verbosity=2).run(suite)
