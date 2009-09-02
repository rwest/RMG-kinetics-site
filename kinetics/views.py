# Create your views here.
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response

#from mysite.kinetics import *

import mysite.kinetics.database
db = mysite.kinetics.database.Database('RMG_Database/kinetics')

def index(request):
    """The index - list of families"""
    families_list = db.getFamiliesList()

    return render_to_response('kinetics/index.html', {'families_list': families_list})

def family(request, family_name):
    
    family = db.getFamily(family_name)
    if family is None:
        raise Http404
    family.load()
    
    return render_to_response('kinetics/family.html', {'family': family})
    
def rate(request, family_name, rate_id):
    family = db.getFamily(family_name)
    if family is None:
        raise Http404
    family.load()
    rate = family.getRate(rate_id)
    comment_list = family.getCommentList()
    comment = comment_list[rate_id.strip('.')]
    return render_to_response('kinetics/rate.html',
        {'family': family, 'rate': rate, 'comment': comment})