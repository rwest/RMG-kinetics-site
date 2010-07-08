from django.db import models
import time

# Create your models here.
class Mechanism(models.Model):
    name = models.CharField(max_length=60)
    def upload_to(instance, filename):
        return 'visualizer/%s/%s'%(instance.pk, filename)
    chemkin_file = models.FileField(upload_to=upload_to)
    dictionary_file = models.FileField(upload_to=upload_to)
    cantera_file = models.FileField(upload_to=upload_to)
    cantera_validated = models.BooleanField()
    cantera_validation_log_file = models.FileField(upload_to=upload_to)
    reactions_imported = models.BooleanField()
    pictures_drawn = models.BooleanField()
    
    
    def get_directory_path(self):
        """
        The path to the directory containing all the files associated with this mechanism.
        """
        mechanism_dir = 'visualizer/%s/'%self.pk
        return os.path.join(settings.MEDIA_ROOT, mechanism_dir)
        
    def __unicode__(self):
        return self.name

class Reaction(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    equation = models.CharField(max_length=200)
    comment = models.CharField(max_length=200)
    number = models.IntegerField()
    #unidentified_species = models.IntegerField()
    reaction_family = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.equation

class Species(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    number = models.IntegerField()
    name = models.CharField(max_length=60)
    smiles = models.CharField(max_length=60)
    identified = models.BooleanField()
    
    def __unicode__(self):
        return self.name

class Reactants(models.Model):
    reaction = models.ForeignKey(Reaction)
    species = models.ForeignKey(Species)
    stoichiometry = models.IntegerField()
    
class Products(models.Model):
    reaction = models.ForeignKey(Reaction)
    species = models.ForeignKey(Species)
    stoichiometry = models.IntegerField()