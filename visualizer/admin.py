from RMG_site.visualizer.models import Mechanism, Reaction, Species
from django.contrib import admin


class MechanismAdmin(admin.ModelAdmin):
    fields = ['name', 'chemkin_file', 'dictionary_file']
    list_display = ('name', 'chemkin_file', 'dictionary_file')

admin.site.register(Mechanism, MechanismAdmin)

admin.site.register(Reaction)

class SpeciesAdmin(admin.ModelAdmin):
    fields = ['number', 'name', 'smiles']
    list_display = ('number', 'name', 'smiles')
admin.site.register(Species, SpeciesAdmin)