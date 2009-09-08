
from settings import *

DEBUG = TEMPLATE_DEBUG = False

SEND_BROKEN_LINK_EMAILS = True

SERVER_EMAIL = 'rmg_devs+server@mit.edu'

RMG_PATH = os.path.realpath( os.path.join(PROJECT_PATH,'..','..','rmg','source') )

ALLOWED_INCLUDE_ROOTS = ('/home/www-data', '/var/www')
# A tuple of strings representing allowed prefixes for the {% ssi %} template tag. This is a security measure, so that template authors can't access files that they shouldn't be accessing.
# For example, if ALLOWED_INCLUDE_ROOTS is ('/home/html', '/var/www'), then {% ssi /home/html/foo.txt %} would work, but {% ssi /etc/passwd %} wouldn't.