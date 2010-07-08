from RMG_site.visualizer.models import Mechanism
from django.contrib import admin


class MechanismAdmin(admin.ModelAdmin):
    fields = ['name', 'chemkin_file', 'dictionary_file']
    list_display = ('name', 'chemkin_file', 'dictionary_file')

admin.site.register(Mechanism, MechanismAdmin)