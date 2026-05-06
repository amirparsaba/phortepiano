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
    
class MusicSheet(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="music_sheets"
    )
    title = models.CharField(max_length=200)                     
    composer = models.CharField(max_length=200)                  
    arranger = models.CharField(max_length=200, blank=True)      
    genre = models.CharField(max_length=100)                     
    content = models.TextField(blank=True)                   
    tags = models.CharField(max_length=500, blank=True)          
    attachment = models.FileField(upload_to='music_sheets/', blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)

    LEVEL_CHOICES = [
        ('beginner', 'مبتدی'),
        ('intermediate', 'متوسط'),
        ('advanced', 'پیشرفته'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='intermediate')
    file_size = models.CharField(max_length=20, blank=True)

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

class Comment(models.Model):
    sheet = models.ForeignKey(MusicSheet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Comment by {self.author.username} on {self.sheet.title}"


    