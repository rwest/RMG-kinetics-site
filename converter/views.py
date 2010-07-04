# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.conf import settings

from RMG_site.converter.models import Mechanism, Reaction, MechanismForm



def index(request):
    all_mechanisms = Mechanism.objects.all()
    form = MechanismForm()
    return render_to_response('mechanisms_list.html', {'mechanisms_list': all_mechanisms, 'form': form })

def new(request):
    if False:
        heading = "Invalid Mechanism"
        message = "You failde to make a new mechanism"
        return render_to_response('blank.html', {'heading':heading, 'message':message})
    else:
        f = MechanismForm(request.POST)
        new_mechanism = f.save()
        return HttpResponseRedirect(reverse('RMG_site.converter.views.mechanism',args=(new_mechanism.id,)))
    
def mechanism(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) # pk is shortcut for primary key, in this case 'id'
    return render_to_response('mechanism.html', {'mechanism': m})

def reactions(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id)
    reactions = get_list_or_404(Reaction, mechanism=m)

    return HttpResponse("You're looking at the reactions of mechanism %s. %s" % (mechanism_name, reactions ))

def reaction(request, mechanism_name, reaction_id):
    return HttpResponse("You're editing reaction %s of mechanism %s." % (reaction_id,mechanism_name))