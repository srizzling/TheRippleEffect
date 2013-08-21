import os, sys

path = '/vol/ecs/sites/wainz'

if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
