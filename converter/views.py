# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.conf import settings

from RMG_site.converter.models import Mechanism, Reaction
from RMG_site.converter.forms import NewMechanismForm, UploadMechanismForm

import converter

def mechanisms_list(request):
    all_mechanisms = Mechanism.objects.all()
    
    if request.method == 'POST': # If the form has been submitted...
        form = NewMechanismForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            m = form.save()
            return HttpResponseRedirect(reverse('RMG_site.converter.views.mechanism',args=(m.id,)))
    else:
        form = NewMechanismForm() # An unbound form
    
    return render_to_response('converter/mechanisms_list.html', {'mechanisms_list': all_mechanisms, 'form': form })

def new(request):
    try:
        f = NewMechanismForm(request.POST)
        m = f.save()
    except ValueError:
        heading = "Invalid Mechanism"
        message = "I failed to make a new mechanism for you."
        if settings.DEBUG: raise
        return render_to_response('converter/blank.html', {'heading':heading, 'message':message})
    return HttpResponseRedirect(reverse('RMG_site.converter.views.mechanism',args=(m.id,)))


def upload(request, mechanism_id):
    try:
        m = get_object_or_404(Mechanism, pk=mechanism_id)
        f = UploadMechanismForm(request.POST,request.FILES, instance=m)
        m = f.save()
    except ValueError:
        heading = "Invalid Mechanism"
        message = "You failed to make a new mechanism"
        if settings.DEBUG: raise
        return render_to_response('converter/blank.html', {'heading':heading, 'message':message})
    return HttpResponseRedirect(reverse('RMG_site.converter.views.mechanism',args=(m.id,)))


def ck2cti(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) 
    converter.convert_chemkin_to_cantera(m)
    return HttpResponseRedirect(reverse('RMG_site.converter.views.mechanism',args=(m.id,)))

def mechanism(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id) # pk is shortcut for primary key, in this case 'id'
    form = UploadMechanismForm(instance=m)
    return render_to_response('converter/mechanism.html', {'mechanism': m, 'form': form})

def reactions(request, mechanism_id):
    m = get_object_or_404(Mechanism, pk=mechanism_id)
    reactions = get_list_or_404(Reaction, mechanism=m)

    return HttpResponse("You're looking at the reactions of mechanism %s. %s" % (mechanism_name, reactions ))

def reaction(request, mechanism_name, reaction_id):
    return HttpResponse("You're editing reaction %s of mechanism %s." % (reaction_id,mechanism_name))