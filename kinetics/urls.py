from django.conf.urls.defaults import *

urlpatterns = patterns('mysite.kinetics.views',

    (r'^$', 'index'),
    (r'^(?P<family_name>[^/]+)/$', 'family'),
    (r'^(?P<family_name>[^/]+)/(?P<rate_id>[^/]+)/$', 'rate')
    
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
