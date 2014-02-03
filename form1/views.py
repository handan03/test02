from django.http import HttpResponse
from forms import MyModelForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from form1.contactform import ContactForm

def create_a_my_model(request):
        if request.method == 'POST':
            form = MyModelForm(request.POST)
            if form.is_valid():
                my_model.save()
        else:        
            form = MyModelForm()
        c = { 'form' : form }
        return HttpResponse('templtate.html', c)
'''
def create_a_my_model(request):
    if request.method == 'POST':
        form = MyModelForm(request.POST)
        if form.is_valid():
            my_model = MyModel()
            my_model.field1 = form.cleaned_data.get('form_field1', 'default1')
            my_model.field2 = form.cleaned_data.get('form_field2', 'default2')
            my_model.save()
    else:        
        form = MyModelForm()
    c = { 'form' : form }
    return HttpResponse('templtate.html', c)
'''
def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })
