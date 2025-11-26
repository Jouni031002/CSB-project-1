from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    secret_info = models.TextField()

    def __str__(self):
        return self.name
    
class Note(models.Model):
    title = models.CharField(max_length=100)
    secret_data = models.TextField()

    def __str__(self):
        return self.title
