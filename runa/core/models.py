from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True, default=None)
    name = models.CharField(max_length=32,  unique=True)
