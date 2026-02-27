from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    fav_genre = models.CharField(max_length=30)
    main_instrument = models.CharField(max_length=40)
    registered_date = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)#email auth
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)

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
