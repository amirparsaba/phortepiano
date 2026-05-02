from rest_framework import serializers
from .models import MusicSheet,User,PendingRegistration, Comment
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
import secrets



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "fav_genre", "main_instrument", "registered_date", 
            "email_verified", "is_active", "date_joined",
            "bio", "profile_picture"
        ]
        read_only_fields = [
            "email_verified", "registered_date", "date_joined", "is_active"
        ]
        
class MusicSheetSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MusicSheet
        fields = [
            "id", "author", "title", "composer", "arranger",
            "genre", "content", "tags", "attachment", "published_date",
            "thumbnail_url",
        ]
    def get_thumbnail_url(self, obj):
        if obj.attachment and obj.attachment.name.lower().endswith('.pdf'):
            return f"/sheets/{obj.id}/page/1/"
        
        return None
        
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

class InitiateRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    fav_genre = serializers.CharField(required=False, allow_blank=True)
    main_instrument = serializers.CharField(required=False, allow_blank=True)

class VerifyRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class CompleteRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    fav_genre = serializers.CharField(required=False, allow_blank=True)
    main_instrument = serializers.CharField(required=False, allow_blank=True)

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created_at']