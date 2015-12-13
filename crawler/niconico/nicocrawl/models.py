from django.db import models

class Tag(models.Model):
    tagname = models.CharField(max_length=128,unique=True)

class Query(models.Model):
    query = models.TextField(unique=True,default="")
    is_active = models.IntegerField(default=1)

class Movie(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    thumbnail_url = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    tags = models.ManyToManyField(Tag)
    queries = models.ManyToManyField(Query)

class Queryhistory(models.Model):
    query = models.TextField()
    date  = models.DateField()
    offset = models.IntegerField()
    total= models.IntegerField()
    is_finished = models.IntegerField(default=0)
