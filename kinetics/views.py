# Create your views here.
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response

#from mysite.kinetics import *
from django.conf import settings
import os
import RMG_site.kinetics.database
db = RMG_site.kinetics.database.Database(
    os.path.join(settings.PROJECT_PATH,'RMG_Database','kinetics') )

def index(request):
    """The index - list of families"""
    #import os
    #return HttpResponse(settings.PROJECT_PATH + '\n'+os.getcwd())
    
    families_list = db.families_list
    return render_to_response('index.html', {'families_list': families_list})

def family(request, family_name):
    """A reaction family"""
    family = db.get_family(family_name)
    if family is None:
        raise Http404
    rates_for_table = family.rates
    return render_to_response('family.html', locals() )
    
def rate(request, family_name, rate_id):
    """The details of a reaction rate."""
    family = db.get_family(family_name)
    if family is None:
        raise Http404
    rate = family.get_rate(rate_id)
    rates_for_table = [rate]
    general_comment = family.get_comment('General').strip()
    comment = family.get_comment(rate_id)
    groups=[]
    for group_name in  rate.groups:
        group = dict()
        group['name']=group_name
        group['definition'] = family.dictionary[group_name]
        ancestors = family.tree.ancestors(group_name)
        ancestors.reverse()
        group['ancestors'] = ancestors
        groups.append(group)
        del(ancestors)
        del(group)
    return render_to_response('rate.html', locals() ) # pass everything in local namespace
       # {'family': family, 'rate': rate, 'comment': comment, 'general_comment': general_comment})

def comments(request, family_name):
    family = db.get_family(family_name)
    comments = file(family.path_to('comments.rst')).read()
    return render_to_response('comments.html',
        {'family': family,'comments': comments})

def convert(request):
    db.convert_comments_to_rST()
    return HttpResponse("Converted all comments.txt files to comments.rst files")