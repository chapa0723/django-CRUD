from django.db import models

# Create your models here.

def UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email= models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.user.username