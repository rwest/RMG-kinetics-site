from django.conf.urls.defaults import *

urlpatterns = patterns('RMG_site.kinetics.views',
    (r'^$',                                     'index'),
    (r'^convert$',                              'convert'),
    (r'^(?P<family_name>[^/]+)/$',              'family'),
    (r'^(?P<family_name>[^/]+)/comments/$',     'comments'),
    (r'^(?P<family_name>[^/]+)/(?P<rate_id>[^/]+)/$', 'rate'),

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