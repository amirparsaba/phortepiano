from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class User(models.Model):
    username = models.CharField(max_length=40)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    fav_genre = models.CharField(max_length=30)
    main_instrument = models.CharField(max_length=40)
    registered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
