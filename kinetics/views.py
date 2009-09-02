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
    """A reaction family"""
    family = db.getFamily(family_name)
    if family is None:
        raise Http404
    family.load()
    rates_for_table = family.rates
    return render_to_response('kinetics/family.html', locals() )
    
def rate(request, family_name, rate_id):
    """THe details of a reaction rate."""
    family = db.getFamily(family_name)
    if family is None:
        raise Http404
    family.load()
    rate = family.getRate(rate_id)
    rates_for_table = [rate]
    comment_list = family.getCommentList()
    general_comment = comment_list['General'].strip()
    comment = comment_list[rate_id]
    return render_to_response('kinetics/rate.html', locals() )
       # {'family': family, 'rate': rate, 'comment': comment, 'general_comment': general_comment})

def comments(request, family_name):
    family = db.getFamily(family_name)
    comments = file(family.path_to('comments.rst')).read()
    return render_to_response('kinetics/comments.html',
        {'family': family,'comments': comments})

def convert(request):
    db.convert_comments_to_rST()
    return HttpResponse("Converted all comments.txt files to comments.rst files")