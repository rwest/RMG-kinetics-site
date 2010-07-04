from models import Mechanism, Reaction, Species, Stoichiometry
import re
import os

from django.conf import settings
from django.core.files import File

def split_chemkin_into_reactions(mechanism):
    """Split a chemkin file into a bunch of reactions"""
    ck = mechanism.chemkin_file.open()
    start_regex = re.compile('^REACTIONS')

def convert_chemkin_to_cantera(mechanism):
    """
    Convert the Chemkin file into a Cantera file.
    
    Does its work inside the folder containing the chemkin file.
    """
    
    from Cantera import ck2cti
    starting_dir = os.getcwd()
    chemkin_dir, infile = os.path.split(mechanism.chemkin_file.name)
    cantera_filename = os.path.splitext(infile)[0]+'.cti'
    chemkin_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, chemkin_dir))
    os.chdir(chemkin_dir)
    if os.path.exists('ck2cti-validation-failed.log'): os.remove('ck2cti-validation-failed.log')
    try:
        thermodb = ''
        trandb = ''
        nm = mechanism.name
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=1)
    except:
        print "Conversion from chemkin to cantera did not validate. Trying again without validation."
        os.rename('ck2cti.log', 'ck2cti-validation-failed.log')
        print "Check",os.path.join(chemkin_dir,'ck2cti-validation-failed.log')
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=0)
    finally:
        os.chdir(starting_dir)
    
    mechanism.cantera_file = File(open(os.path.join(chemkin_dir,cantera_filename)))
    mechanism.save()