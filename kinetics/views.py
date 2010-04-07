# Create your views here.
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response

#from mysite.kinetics import *
from django.conf import settings
import os
import RMG_site.kinetics.database
db = RMG_site.kinetics.database.Database(
    os.path.join(settings.PROJECT_PATH,'RMG_Database','kinetics_groups') )

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

def family_python(request, family_name):
    """A reaction family, rendered in python"""
    family = db.get_family(family_name)
    if family is None:
        raise Http404
    rates_for_table = family.rates

    for rate in rates_for_table:
        rate.group_definitions = list()
        for group_name in  rate.groups:
            rate.group_definitions.append(family.dictionary[group_name])
        rate.long_comment = family.get_comment(rate.id)

    return render_to_response('family_python.html', locals() )
    
def rate(request, family_name, rate_id):
    """The details of a reaction rate."""
    family = db.get_family(family_name)
    if family is None:
        raise Http404
    rate = family.get_rate(rate_id)
    rates_for_table = [rate]
    general_comment = family.get_comment('General').strip()
    comment = family.get_comment(rate_id)
    groups=[] # a list (of dictionaries) that we pass to the template
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


def tree(request, family_name):
    family = db.get_family(family_name)
    return render_to_response('tree.html', locals() ) # pass everything in local namespace

def comments(request, family_name):
    family = db.get_family(family_name)
    comments = file(family.path_to('comments.rst')).read()
    return render_to_response('comments.html',
        {'family': family,'comments': comments})

def convert_to_rST(request):
    db.convert_comments_to_rST()
    heading = "Convert Comments"
    message = "Converted all comments.txt files to comments.rst files"
    return render_to_response('blank.html', {'heading':heading, 'message':message})
    
def convert_to_py(request):
    import codecs # to write unicode file
    """Convert the database libraries into the python syntax"""
    heading = "Convert Comments"
    message = "Converted rateLibrary.txt files to library.py files:"
    
    pytemplate = loader.get_template('table.py')
    try:
        for family in db.families_list:
            if not os.path.exists(family.path_to('rateLibrary.txt')): 
                message += "<li>Skipping %s because no rateLibrary.txt found</li>\n"%family.name
                continue
            in_file = file(family.path_to('rateLibrary.txt'))
            out_file = codecs.open(family.path_to('library.py'),'w',"utf-8" )
            #out_file = file(family.path_to('library.py'),'w')
            rates_for_table = family.rates
            for rate in rates_for_table:
                rate.group_definitions = list()
                for group_name in  rate.groups:
                    if group_name.startswith('Others-') and not family.dictionary.has_key(group_name):
                        rate.group_definitions.append(group_name+'\n') # no definition
                    else:
                        rate.group_definitions.append(family.dictionary[group_name])
                rate.long_comment = family.get_comment(rate.id)
            
            context = Context( locals() )
            rate_response = pytemplate.render( context )
            out_file.write(rate_response)
            in_file.close()
            out_file.close()
            message += "<li>Done %s</li>\n"%family.name
    except Exception, e:
        message += "<li>FAILED on %s</li>\n"%family.name
        message += repr(e)
        # write what you have so far
        context = Context( locals() )
        rate_response = pytemplate.render( context )
        out_file.write(rate_response)
        in_file.close()
        out_file.close()
    
    return render_to_response('blank.html', {'heading':heading, 'message':message, 'message_safe':True})


def update(request):
   # import cvs
    import commands
    heading = "Update from CVS"
    message = "Updating from cvs server.."
    message+="<pre>"
    dbpath=os.path.join(settings.PROJECT_PATH,'RMG_Database','kinetics')
    message+=commands.getoutput('cd %s; cvs -q update'%dbpath)
    message+="</pre>"
    db.load()
    return render_to_response('blank.html', {'heading':heading, 'message':message, 'message_safe':True})