from django.conf.urls import patterns, url
from form1 import views
#from form1 import contactform

urlpatterns = patterns('',
        url(r'^$', views.create_a_my_model, name='form1'),
        #url(r'^contactform/$', contactform.ContactForm, name='contactform'),
        url(r'^contact/$', views.contact, name='contact'),

)
