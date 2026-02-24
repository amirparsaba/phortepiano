from rest_framework import serializers
from .models import BlogPost,User

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    class Meta:
        model = BlogPost
        fields = ["id", "author", "title", "content", "published_date"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "fav_genre", "main_instrument", "registered_date"]
        