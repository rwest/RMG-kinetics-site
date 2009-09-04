# this code from github, but seems to be based (very closely) on this post:
# http://www.djangosnippets.org/snippets/1061/
# Integration of django and Jinja2.
# 
# Just import render_to_response from this file and you are ready.
# 
# This file automatically adds template search path from your
# TEMPLATE_DIRS and from each installed application.
# 
# You can also use several variables in your settings.py to add 
# filters, tests and global functions to the default context. 
# This can be done by using JINJA_GLOBALS, JINJA_FILTERS and JINJA_TEST 
# e.g. JINJA_FILTERS = ( 'myapp.filters.myfilter', 'myapp.filters.myfilter2', )

from django.http import HttpResponse
from django.conf import settings
from jinja2 import PackageLoader, Environment, ChoiceLoader, FileSystemLoader
from django.core.urlresolvers import get_callable
from django.utils import translation
from django.utils.thread_support import currentThread

global env

# Setup template loaders
loader_array = (map(FileSystemLoader, getattr(settings, 'TEMPLATE_DIRS', ())) +
                map(PackageLoader, settings.INSTALLED_APPS))
                
# Setup environment
default_mimetype = getattr(settings, 'DEFAULT_CONTENT_TYPE')
global_exts = getattr(settings, 'JINJA_EXTS', ())
env = Environment(extensions=global_exts, loader=ChoiceLoader(loader_array))

if 'jinja2.ext.i18n' in global_exts:
    env.install_gettext_translations(translation)

# Add user Globals, Filters, Tests
for name in ('globals', 'filters', 'tests'):
    for imp in getattr(settings, 'JINJA_' + name.upper(), ()):
        method = get_callable(imp)
        method_name = getattr(method, 'jinja_name', None)
        in_env = getattr(env, name)
        if not method_name == None:
            in_env[method_name] = method
        else:
            in_env[method.__name__] = method

def render_to_string(filename, context={}):
    template = env.get_template(filename)
    rendered = template.render(**context)
    return rendered

def render_to_response(filename, context={}, request=None, mimetype=default_mimetype):
    if request:
        context['request'] = request
    rendered = render_to_string(filename, context)
    return HttpResponse(rendered, mimetype=mimetype)
