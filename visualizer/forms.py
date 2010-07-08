from django.forms import ModelForm

from models import Mechanism

# Form for creating new mechanism
class NewMechanismForm(ModelForm):
    class Meta:
        model = Mechanism
        fields = ('name',)
        
class UploadMechanismForm(ModelForm):
    class Meta:
        model = Mechanism
        fields = ('chemkin_file', 'dictionary_file',)
