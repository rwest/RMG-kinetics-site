from RMG_site.converter.models import Mechanism
from django.contrib import admin


class MechanismAdmin(admin.ModelAdmin):
    fields = ['name', 'chemkin_file']
    list_display = ('name', 'chemkin_file')

admin.site.register(Mechanism, MechanismAdmin)