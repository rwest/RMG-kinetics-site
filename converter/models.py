from django.db import models

# Create your models here.
class Mechanism(models.Model):
    name = models.CharField(max_length=60)
    def upload_to(instance, filename):
        return 'converter/%s/%s'%(instance.pk, filename)
    chemkin_file = models.FileField(upload_to=upload_to)
    cantera_file = models.FileField(upload_to=upload_to)
    
    def __unicode__(self):
        return self.name

class Reaction(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    chemkin_string = models.CharField(max_length=200)
    unidentified = models.IntegerField()
    
    def __unicode__(self):
        return self.chemkin
    

class Species(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    name = models.CharField(max_length=60)
    smiles = models.CharField(max_length=60)
    identified = models.BooleanField()

class Stoichiometry(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    reaction = models.ForeignKey(Reaction)
    species = models.ForeignKey(Species)
    stoichiometry = models.IntegerField()