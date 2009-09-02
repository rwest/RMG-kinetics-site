from django.db import models

# Create your models here.

class Family(models.Model):
    adjlist = models.TextField('The entire adjacency list file')
    
class 

class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField()