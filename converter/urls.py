from django.conf.urls.defaults import *

urlpatterns = patterns('RMG_site.converter.views',
    (r'^$', 'mechanisms_list'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/$', 'mechanism'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/upload/$', 'upload'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/ck2cti/$', 'ck2cti'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/cti2db/$', 'cti2db'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/reactions/$', 'reactions'),
    (r'^mechanisms/(?P<mechanism_id>[^/]+)/reactions/(?P<reaction_id>\d+)$', 'reaction'),
    

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
            {'document_root': os.path.join(settings.PROJECT_PATH, 'converter', 'media'),
            'show_indexes': True,}
        ),
    )