# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.conf import settings

from RMG_site.visualizer.models import Mechanism, Reaction
from RMG_site.visualizer.forms import NewMechanismForm, UploadMechanismForm

import visualizer

def mechanisms_list(request):
    """
    Displays list of existing mechanisms and a form to create a new one.

    Templates: :template:`visualizer/mechanisms_list.html`,
    Context:
        mechanisms_list
            the list of all mechanisms
        form
            the form for creating a new mechanism
    """
    all_mechanisms = Mechanism.objects.all()    
    if request.method == 'POST': # If the form has been submitted...
        form = NewMechanismForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            m = form.save()
            return HttpResponseRedirect(reverse('RMG_site.visualizer.views.mechanism',args=(m.id,)))
    else:
        form = NewMechanismForm() # An unbound form
    return render_to_response('visualizer/mechanisms_list.html', {'mechanisms_list': all_mechanisms, 'form': form })


def upload(request, mechanism_id):
    try:
        m = get_object_or_404(Mechanism, pk=mechanism_id)
        f = UploadMechanismForm(request.POST,request.FILES, instance=m)
        m = f.save()
    except ValueError:
        heading = "Invalid Mechanism"
        message = "You failed to make a new mechanism"
        if settings.DEBUG: raise
        return render_to_response('visualizer/blank.html', {'heading':heading, 'message':message})
    return HttpResponseRedirect(reverse('RMG_site.visualizer.views.mechanism',args=(m.id,)))

def ck2cti(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) 
    visualizer.convert_chemkin_to_cantera(m)
    return HttpResponseRedirect(reverse('RMG_site.visualizer.views.mechanism',args=(m.id,)))
    
def draw_species(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) 
    visualizer.draw_species(m)
    return HttpResponseRedirect(reverse('RMG_site.visualizer.views.mechanism',args=(m.id,)))

def cti2db(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) 
    visualizer.convert_cantera_to_database(m)
    return HttpResponseRedirect(reverse('RMG_site.visualizer.views.mechanism',args=(m.id,)))

def mechanism(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) # pk is shortcut for primary key, in this case 'id'
    form = UploadMechanismForm(instance=m)
    return render_to_response('visualizer/mechanism.html', {'mechanism': m, 'form': form})

def reactions(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id)
    reactions = get_list_or_404(Reaction, mechanism=m)
    return HttpResponse("You're looking at the reactions of mechanism %s. %s" % (m.name, reactions ))

def reaction(request, mechanism_name, reaction_id):
    return HttpResponse("You're editing reaction %s of mechanism %s." % (reaction_id,mechanism_name))