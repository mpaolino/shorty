from shorty import app
# load the middleware from werkzeug
# This middleware can be applied to add HTTP proxy support to an application
# that was not designed with HTTP proxies in mind.
# It sets `REMOTE_ADDR`, `HTTP_POST` from `X-Forwarded` headers.
from werkzeug.contrib.fixers import ProxyFix

try:
    from shorty import settings
except ImportError:
    logging.error('Could not find settings. Aborting...')
    sys.exit(1)

app.config.from_object(settings)

from shorty.routes import *
from shorty.database import init_db
init_db()

app.wsgi_app = ProxyFix(app.wsgi_app)
