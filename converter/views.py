# Create your views here.
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404

from django.conf import settings

from RMG_site.converter.models import Mechanism, Reaction


def index(request):
    all_mechanisms = Mechanism.objects.all()
    return render_to_response('mechanisms_list.html', {'mechanism_list': all_mechanisms})

def mechanism(request, mechanism_name):
    m = get_object_or_404(Mechanism, name=mechanism_name)
    return render_to_response('mechanism.html', {'mechanism': m})

def reactions(request, mechanism_name):
    m = get_object_or_404(Mechanism, name=mechanism_name)
    reactions = get_list_or_404(Reaction, mechanism=m)

    return HttpResponse("You're looking at the reactions of mechanism %s. %s" % (mechanism_name, reactions ))

def reaction(request, mechanism_name, reaction_id):
    return HttpResponse("You're editing reaction %s of mechanism %s." % (reaction_id,mechanism_name))