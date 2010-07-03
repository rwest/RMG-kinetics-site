from django.conf.urls.defaults import *

urlpatterns = patterns('RMG_site.converter.views',
    (r'^$',                                     'index'),
    (r'^(?P<mechanism_name>[^/]+)/$',           'mechanism'),
    (r'^(?P<mechanism_name>[^/]+)/reactions/$',    'reactions'),
    (r'^(?P<mechanism_name>[^/]+)/reactions/(?P<reaction_id>\d+)$',     'reaction'),

    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

import os
from django.conf import settings
if settings.DEBUG: # not being served by Apache, serve it by Django
    urlpatterns += patterns('',
        (r'^media/(.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.PROJECT_PATH, 'kinetics', 'media'),
            'show_indexes': True,}
        ),
    )