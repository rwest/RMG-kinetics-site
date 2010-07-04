from django.db import models
from django.forms import ModelForm

# Create your models here.
class Mechanism(models.Model):
    name = models.CharField(max_length=60)
    chemkin_file = models.FileField(upload_to='mechanisms')
    
    def __unicode__(self):
        return self.name

# Form for creating new mechanism
class MechanismForm(ModelForm):
    class Meta:
        model = Mechanism
        fields = ('name', 'chemkin_file')

class Reaction(models.Model):
    mechanism = models.ForeignKey(Mechanism)
    chemkin = models.CharField(max_length=200)
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