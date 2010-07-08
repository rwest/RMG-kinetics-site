#! /usr/bin/python
# this version updated by Richard West <rwest@mit.edu> in June 2010
"""
Postprocess a load of RMG Results
"""
import os, sys, shutil, re

# Django stuff for web version
from models import Mechanism, Reaction, Species, Reactants, Products
from django.conf import settings
from django.core.files import File
from RMG_site.converter.django_utils import _ExistingFile # should put somewhere better

# use local modified versions of pybel and oasa
package_path = os.path.join( os.path.split(os.path.realpath(__file__))[0],'python-packages' )
if os.path.exists(package_path):
    sys.path.insert(1,package_path) 


def draw_species(mechanism):
    """Draw pictures of each of the molecules in the RMG dictionary.
    
    Also creates MolarMasses.txt. Puts its results inside RMG_results directory.
    Returns a dictionary of chemkin formulae and a dictionary of smiles strings, indexed by species name.
    """
    import re
    import openbabel, pybel
    # please cite:
    # Pybel: a Python wrapper for the OpenBabel cheminformatics toolkit
    # Noel M O'Boyle, Chris Morley and Geoffrey R Hutchison
    # Chemistry Central Journal 2008, 2:5
    # doi:10.1186/1752-153X-2-5
    
    mechanism_dir, infile = os.path.split(mechanism.dictionary_file.name)
    full_mechanism_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, mechanism_dir))
    RMG_results = full_mechanism_dir
    
    picfolder=os.path.join(RMG_results,'pics')
    pdffolder=os.path.join(RMG_results,'pdfs')
    molfolder=os.path.join(RMG_results,'mols')
    
    for path in [picfolder,molfolder,pdffolder]:
        if os.path.isdir(path):
            print "Removing old contents of '%s'"%path
            for f in os.listdir(path):
                os.remove(os.path.join(path,f))
        else:
            os.makedirs(path)
    print "Making .mol files in '%s' and pictures in '%s' and pdfs in '%s'"%(molfolder,picfolder,pdffolder)
    
    periodicTableByNumber={ 1: 'H',  2: 'He',  3: 'Li',  4: 'Be',  5: 'B',  6: 'C',  7: 'N',  8: 'O',  9: 'F',  10: 'Ne',  11: 'Na',  12: 'Mg',  13: 'Al',  14: 'Si',  15: 'P',  16: 'S',  17: 'Cl',  18: 'Ar',  19: 'K',  20: 'Ca',  21: 'Sc',  22: 'Ti',  23: 'V',  24: 'Cr',  25: 'Mn',  26: 'Fe',  27: 'Co',  28: 'Ni',  29: 'Cu',  30: 'Zn',  31: 'Ga',  32: 'Ge',  33: 'As',  34: 'Se',  35: 'Br',  36: 'Kr',  37: 'Rb',  38: 'Sr',  39: 'Y',  40: 'Zr',  41: 'Nb',  42: 'Mo',  43: 'Tc',  44: 'Ru',  45: 'Rh',  46: 'Pd',  47: 'Ag',  48: 'Cd',  49: 'In',  50: 'Sn',  51: 'Sb',  52: 'Te',  53: 'I',  54: 'Xe',  55: 'Cs',  56: 'Ba',  57: 'La',  58: 'Ce',  59: 'Pr',  60: 'Nd',  61: 'Pm',  62: 'Sm',  63: 'Eu',  64: 'Gd',  65: 'Tb',  66: 'Dy',  67: 'Ho',  68: 'Er',  69: 'Tm',  70: 'Yb',  71: 'Lu',  72: 'Hf',  73: 'Ta',  74: 'W',  75: 'Re',  76: 'Os',  77: 'Ir',  78: 'Pt',  79: 'Au',  80: 'Hg',  81: 'Tl',  82: 'Pb',  83: 'Bi',  84: 'Po',  85: 'At',  86: 'Rn',  87: 'Fr',  88: 'Ra',  89: 'Ac',  90: 'Th',  91: 'Pa',  92: 'U',  93: 'Np',  94: 'Pu',  95: 'Am',  96: 'Cm',  97: 'Bk',  98: 'Cf',  99: 'Es',  100: 'Fm',  101: 'Md',  102: 'No',  103: 'Lr',  104: 'Rf',  105: 'Db',  106: 'Sg',  107: 'Bh',  108: 'Hs',  109: 'Mt',  110: 'Ds',  111: 'Rg',  112: 'Uub',  113: 'Uut',  114: 'Uuq',  115: 'Uup',  116: 'Uuh',  117: 'Uus',  118: 'Uuo'}
    periodicTableBySymbol=dict([(val, key) for key, val in periodicTableByNumber.items()])   
    OBMolBondTypes={'S':1, 'D':2, 'T':3, 'B':5 }
    
    infile='RMG_Dictionary.txt'
    path=os.path.join(RMG_results,infile)
    RMGfile=file(path)
    
    masses=file(os.path.join(RMG_results,'MolarMasses.txt'),'w')
    
    chemkin_formulae = dict()
    smiless = dict()
    
    for i in range(1,30000): # only does 30,000 [core] molecules
        print 'Molecule', i,'\t',
        name=''
        try:
            while name=='':
                name=RMGfile.next().strip()
        except StopIteration:
            print 'No more molecules'
            break
        print '%-18s'%name ,
        graph=[]
        line=RMGfile.next()
        while line.strip():
            graph.append(line)
            line=RMGfile.next()
        # now have 'name' and 'graph'
    
        mol = openbabel.OBMol()
        re_bond=re.compile('\{(?P<atomnum>\d+),(?P<bondtype>[SDTB])\}')
        atoms_by_rmg_number = dict() # the atom numbers apparently don't have to be 1,2,3.. so we need a dictionary 
        for line in graph:
            #print 'line:',line.strip()
            if len(line.split())>3:
                (number, element, radical, bonds)=line.split(None,3)
            else:
                (number, element, radical )=line.split(None)
            a = mol.NewAtom()
            atoms_by_rmg_number[int(number)] = a.GetIdx()
            a.SetAtomicNum(periodicTableBySymbol[element])  # 6 for a carbon atom
            if int(radical[0]): # the [0] is so we take the first character of the string, in case it's something like "2T"
                a.SetSpinMultiplicity(int(radical[0])+1)
                # note that for non-radicals it's 0, but single radicals are 2, double radicals are 3...
                # http://openbabel.org/wiki/Radicals_and_SMILES_extensions#How_OpenBabel_does_it
            for bond in bonds.split():
                matchobject=re_bond.match(bond)
                if matchobject:
                    fromAtom=int(number)
                    toAtom=int(matchobject.group('atomnum'))
                    bondType=matchobject.group('bondtype')
                    if toAtom>fromAtom:
                        continue # because toAtom hasn't been placed yet!
                    # print "%s bond from %d to %d"%(bondType,fromAtom,toAtom)
                    mol.AddBond(atoms_by_rmg_number[fromAtom],atoms_by_rmg_number[toAtom],OBMolBondTypes[bondType])
                else:
                    raise "couldn't figure out this bond: %s"%bond
        pymol=pybel.Molecule(mol)
        smiles = pymol.write('smi').strip()
        print '%-18s'%smiles, 
        chemkinformula=pymol.formula+'J'*(pymol.spin-1)
        print chemkinformula
        if pymol.OBMol.NumHvyAtoms()>1:
            pymol.removeh()
        pymol.draw(filename=os.path.join(picfolder,name+'.png'), update=True, show=False)
        #pymol.draw(filename=os.path.join(pdffolder,name+'.pdf'), update=False, show=False)
        #pymol.write(format='mol',filename=os.path.join(molfolder,name+'.mol'),overwrite=True)
        
        masses.write(name+'\t'+str(pymol.exactmass)+'\n')

        chemkin_formulae[name]=chemkinformula
        smiless[name] = smiles
        
        # add species to the django database
        try: # check if it's already there
            S = Species.objects.get(mechanism=mechanism, name=name)
        except Species.DoesNotExist:
            S = Species(mechanism=mechanism, name=name, number=0)
        S.smiles = smiles
        S.save()
    
    masses.close()
    RMGfile.close()
    mechanism.pictures_drawn = True
    mechanism.save()
    return chemkin_formulae, smiless

def convert_chemkin_to_cantera(mechanism):
    """
    Convert the Chemkin file into a Cantera file.
    
    Does its work inside the folder containing the chemkin file.
    """
    
    from Cantera import ck2cti
    starting_dir = os.getcwd()
    mechanism_dir, infile = os.path.split(mechanism.chemkin_file.name)
    cantera_filename = os.path.splitext(infile)[0]+'.cti'
    full_mechanism_dir = os.path.realpath(os.path.join(settings.MEDIA_ROOT, mechanism_dir))
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
    
def convertChemkin2Cantera(RMG_results):
    """
    Convert the Chemkin file into a Cantera file.
    
    Does its work inside RMG_results/chemkin
    """
    
    from Cantera import ck2cti
    starting_dir = os.getcwd()
    chemkin_dir = os.path.join(RMG_results,'chemkin')
    infile='chem.inp'
    
    print "Converting chemkin file '%s' into cantera file '%s' in folder '%s/'"%(infile,
        os.path.splitext('chem.inp')[0]+'.cti', chemkin_dir)
    
    os.chdir(chemkin_dir)
    if os.path.exists('ck2cti-validation-failed.log'): os.remove('ck2cti-validation-failed.log')
    try:
        thermodb=''
        trandb=''
        nm='chem'
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=1)
    except:
        print "Conversion from chemkin to cantera did not validate. Trying again without validation."
        os.rename('ck2cti.log', 'ck2cti-validation-failed.log')
        print "Check",os.path.join(chemkin_dir,'ck2cti-validation-failed.log')
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=0)
    finally:
        os.chdir(starting_dir)

def convertFinalModel2MixMaster(RMG_results):
    """Convert the Final_Model.txt into appropriate CSV data file for mixmaster.
    
    Needs a MolarMasses.txt file, which is created in another function.
    Returns True if it suceeds, False if it fails."""
    
    # load file
    filename ='Final_Model.txt'
    filepath = os.path.join(RMG_results,filename)
    outputfilepath = os.path.join(RMG_results,'ForMixMaster.csv')
    
    print "Converting mole fractions profile from '%s' into mass fractions profile in '%s'"%(filename, outputfilepath)
    
    try:
        resultFile=file(filepath)
    except IOError:
        print "Couldn't open '%s'."%filepath
        print "Will therefore not create mass fractions profile in '%s'"%outputfilepath
        if os.path.exists(outputfilepath): 
            print "In fact, I'm going to delete the old one for you, as it's out of date."
            os.remove(outputfilepath)
        return False
    
    massesfilename=os.path.join(RMG_results,'MolarMasses.txt')
    print "Reading molar masses from",massesfilename
    massesfile=file(massesfilename)
    massesdict=dict()
    for line in massesfile:
        (species,mass)=line.split()
        massesdict[species]=mass
    massesfile.close()
    
    temperature=273+150
    pressure=208*101325
    print "Using these settings:\n Temperature: %f K \t Pressure: %f Pa\n"%(temperature,pressure)
    
    # search for "Mole Fraction Profile Output"
    line=resultFile.next()
    while (line.find('Mole Fraction Profile Output')<0):
        line=resultFile.next()
    # add "T \t P" to the  following line
    titles=resultFile.next()
    print "Species:",titles
    output=titles.strip()+"\tT\tP\tnothing\n"
    items=titles.split()
    assert items[0]=='Time'
    speciesnames=items[1:]
    masses=list()
    for species in speciesnames:
        masses.append(float(massesdict[species]))
    	
    # add the temperature IN KELVIN and pressure IN PASCAL to all the following nonblank lines
    line=resultFile.next()
    while (line.strip()):
        massfractions=[]
        massfractionsum = 0
        items = line.split()
        time = items[0]
        molefracs = items[1:]
        for i,molefrac in enumerate(molefracs):
            massfrac = float(molefrac)*masses[i]
            massfractions.append(massfrac)
            massfractionsum += massfrac
        massfractions = [str(m/massfractionsum) for m in massfractions]
        output += str(time)+'\t'
        output += '\t'.join(massfractions)
        output +=  "\t%f\t%f\t0\n"%(temperature,pressure)
        line=resultFile.next()
    # turn whitespaces into commas
    # save the output
    outputFile=file(outputfilepath,'w')
    outputFile.write(output.replace('\t',','))
    outputFile.close()
    print "ForMixMaster.csv now contains mass fractions, as required by MixMaster"
    return True
    

def convert_cantera_to_database(mechanism):
    """Convert the cantera file into the database entries"""

    import ctml_writer
    #from ctml_writer import * 
    # if you're not allowed to import * then you'll need at least these:
    from ctml_writer import units, ideal_gas, state, OneAtm, species, NASA, \
        reaction, falloff_reaction, three_body_reaction, Troe
    
    # these lists store top-level entries. Empty them:
    ctml_writer._elements = []
    ctml_writer._species = []
    ctml_writer._speciesnames = []
    ctml_writer._phases = []
    ctml_writer._reactions = []
    ctml_writer._atw = {}
    ctml_writer._enames = {}
    ctml_writer._valsp = ''
    ctml_writer._valrxn = ''
    ctml_writer._valexport = ''
    ctml_writer._valfmt = ''
    
    mechanism.cantera_file.open()
    cti_file = mechanism.cantera_file.read()
    mechanism.cantera_file.close()
    #local_context = { '__builtins__':None,
    #                  '_rates': _rates,
    #                  'rate': rate,
    #                  'Arrhenius':Arrhenius,
    #                  'Parameter':Parameter,
    #                }
    #global_context = {'__builtins__':None,
    # TODO: check library_file is safe. Perhaps with http://code.activestate.com/recipes/496746-restricted-safe-eval/
    # although I think limiting the context as above may be ample protection
    # for now lets be unsafe:
    local_context = locals()
    global_context = globals()
    try:
        exec cti_file in global_context, local_context
    except NameError, e:
        logging.error("Looks like the file %s had an illegal operator in it:"%mechanism.cantera_file.name )
        logging.error(e)
        raise
    #finally:
    #    mechanism.cantera_file.close()
    # _rates = local_context['_rates']
    
    comments=list()
    next_line_is_reaction = False
    mechanism.cantera_file.open()
    for line in mechanism.cantera_file:
        if not line.startswith('#'): continue
        if next_line_is_reaction:
            comments.append(line[2:].strip())
        if re.match('#  Reaction (\d+)',line):
            next_line_is_reaction = True
            reaction_number = line.split()[-1]
        else: 
            next_line_is_reaction = False
    mechanism.cantera_file.close()
    assert len(comments) == len(ctml_writer._reactions)
    
    families = set()
    for i,comment in enumerate(comments):
        ctml_writer._reactions[i].comment = comment
        family = comment.split()[0]
        ctml_writer._reactions[i].family = family
        families.add(family)
        #import pdb; pdb.set_trace()

    # add species to the django database
    for i,s in enumerate(ctml_writer._species):
        try: # check if it's already there
            S = Species.objects.get(mechanism=mechanism, name=s._name)
        except Species.DoesNotExist:
            S = Species(mechanism=mechanism, name=s._name)
        S.number = i+1
       # S.atoms = repr(s._atoms) # s._atoms is a dict
       # S.unidentified_species=99
        S.save()
        
    # add reactions to the django database
    for i,r in enumerate(ctml_writer._reactions):
        R = Reaction(number=i+1, mechanism=mechanism)
        R.equation=r._e
        R.unidentified_species=99
        R.reaction_family = r.family
        R.comment = r.comment
        R.save() # we need a reaction.id before we can add the stoichiometry info
        for reactant,stoich in r._r.iteritems():
            R.reactants_set.create(species=Species.objects.get(name=reactant, mechanism=mechanism), stoichiometry=stoich)
        for product,stoich in r._p.iteritems():
            R.products_set.create(species=Species.objects.get(name=product, mechanism=mechanism), stoichiometry=stoich)
    
    mechanism.reactions_imported = True
    mechanism.save()

def loadMixMaster(RMG_results):
    """Load MixMaster"""
    os.path.chdir(RMG_results)
    from MixMaster import MixMaster
    o=MixMaster()
    o.loadmech('','chem.cti')
    
if __name__ == "__main__":
    import optparse
    usage = "usage: %prog [options] rmg_results_path"
    parser = optparse.OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print "Please specify an rmg results path"
    else:
        RMG_results = args[0]
        
        print "Processing results in ",os.path.realpath(RMG_results)
        chemkin_formulae, smiless = drawMolecules(RMG_results)
        convertChemkin2Cantera(RMG_results)
        makeTableOfReactions(RMG_results, chemkin_formulae, smiless)
        convertFinalModel2MixMaster(RMG_results)
