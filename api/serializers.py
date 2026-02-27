from rest_framework import serializers
from .models import BlogPost,User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
import secrets


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    
    class Meta:
        model = BlogPost
        fields = ["id", "author", "title", "content", "published_date"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "fav_genre", "main_instrument", "registered_date", 
            "email_verified", "is_active", "date_joined"
        ]
        read_only_fields = [
            "email_verified", "registered_date", "date_joined", "is_active"
        ]
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'password', 'password2', 'email',
            'first_name', 'last_name', 'fav_genre', 'main_instrument'
        ]
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": " ! رمز عبور و تکرار آن مطابقت ندارند"})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "این ایمیل قبلا ثبت شده است"})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        
        #email auth- token creation
        email_token = secrets.token_urlsafe(32)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            fav_genre=validated_data.get('fav_genre', ''),
            main_instrument=validated_data.get('main_instrument', ''),
            email_verification_token=email_token,
            is_active=True,
        )
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()