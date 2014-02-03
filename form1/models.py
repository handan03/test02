from django.db import models

class MyModel(models.Model):
    field1 = models.CharField(max_length=40, blank=False, null=False)
    field2 = models.CharField(max_length=60, blank=True, null=True)
