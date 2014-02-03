from django.contrib import admin
from rango.models import Category, Page
# Import the UserProfile model individually.
from rango.models import UserProfile

admin.site.register(Category)
# admin.site.register(Page)

class PageAdmin(admin.ModelAdmin):
    #fields = ['pub_date', 'question']
    list_display = ('title', 'category', 'url')
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
