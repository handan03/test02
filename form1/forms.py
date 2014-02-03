from django.forms import ModelForm
#from django import forms
from form1.models import MyModel

class MyModelForm(ModelForm):
    class Meta:
        model = MyModel
'''
class MyModelForm(forms.Form):
    form_field1 = forms.CharField(max_length=40, required=True)
    form_field2 = forms.CharField(max_length=60, required=False)
'''
