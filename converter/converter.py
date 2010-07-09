from models import Mechanism, Reaction, Species, Stoichiometry
import re
import os

from django.conf import settings
from django.core.files import File

from django_utils import _ExistingFile

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
    mechanism_dir, infile = os.path.split(mechanism.chemkin_file.name)
    cantera_filename = os.path.splitext(infile)[0]+'.cti'
    full_mechanism_dir = os.path.realpath(mechanism.get_directory_path() )
    os.chdir(full_mechanism_dir)
    if os.path.exists('ck2cti-validation-failed.log'): os.remove('ck2cti-validation-failed.log')

    thermodb = ''
    trandb = ''
    nm = mechanism.name
    try:
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=1)
    except:
        print "Conversion from chemkin to cantera did not validate. Trying again without validation."
        os.rename('ck2cti.log', 'ck2cti-validation-failed.log')
        print "Check",os.path.join(mechanism_dir,'ck2cti-validation-failed.log')
        mechanism.cantera_validated = False
        mechanism.cantera_validation_log_file.save('ck2cti-validation-failed.log',_ExistingFile(os.path.join(full_mechanism_dir,'ck2cti-validation-failed.log')))
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=0)
    else:
        mechanism.cantera_validated = True
        mechanism.cantera_validation_log_file.save('ck2cti.log',_ExistingFile(os.path.join(full_mechanism_dir,'ck2cti.log')))
    finally:
        os.chdir(starting_dir)
    mechanism.cantera_file.save(cantera_filename, _ExistingFile(os.path.join(full_mechanism_dir,cantera_filename)))
    mechanism.save()

def convert_cantera_to_database(mechanism):
    """Convert the cantera file into the database entries"""
    pass