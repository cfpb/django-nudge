from django.db import models

# Create your models here.

class Author(models.Model):
    name=models.CharField(max_length=1000)

class Post(models.Model):
	title=models.CharField(max_length=1000)
	author=models.ForeignKey(Author)
	body=models.TextField()
	
	def __unicode__(self):
	    return self.title




