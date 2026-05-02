from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    fav_genre = models.CharField(max_length=30, blank=True, default='')
    main_instrument = models.CharField(max_length=40, blank=True, default='')
    registered_date = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)#email auth
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username
    
class BlogPost(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
        
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class PendingRegistration(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=128)
    fav_genre = models.CharField(max_length=30, blank=True)
    main_instrument = models.CharField(max_length=40, blank=True)
    verification_code = models.CharField(max_length=6)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.verification_code}"
    