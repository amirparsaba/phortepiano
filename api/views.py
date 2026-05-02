from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q


from .models import BlogPost, User
from .serializers import (
    BlogPostSerializer, UserSerializer, RegisterSerializer,
    LoginSerializer, EmailVerificationSerializer, InitiateRegistrationSerializer, VerifyRegistrationSerializer, CompleteRegistrationSerializer
)
# Swagger needs :
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# User Profile View for picture
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class BlogPostListCreate(generics.ListCreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)# getting author from logined user

    '''def create(self, request, *args, **kwargs):
        author_id = request.data.get("author_id")

        if not author_id:
            return Response(
                {"error": "author_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            author = User.objects.get(id=author_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=author)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    '''
    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "شما اجازه حذف همه پست هارا ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        BlogPost.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BlogPostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    lookup_field = "pk"

class BlogPostList(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="filtered by post",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={200: BlogPostSerializer(many=True)}
    )
    def get(self, request, format=None):

        title = request.query_params.get("title", "")

        if title:
            blog_posts = BlogPost.objects.filter(title__icontains=title)
        else:
            blog_posts = BlogPost.objects.all()

        serializer = BlogPostSerializer(blog_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.request.method == 'post':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "شما اجازه حذف همه کاربران را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        User.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class UserList(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_QUERY,
                description="فیلتر بر اساس نام کاربری",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, format=None):

        username = request.query_params.get("username", "")

        if username:
            Users = User.objects.filter(username__icontains=username)
        else:
            Users = User.objects.all()

        serializer = UserSerializer(Users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        responses={201: UserSerializer()}
    )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # ارسال ایمیل تایید (با استفاده از console backend برای تست)
        verification_link = f"http://localhost:8000/api/verify-email/?token={user.email_verification_token}"
        
        subject = "تایید ایمیل در وبسایت موسیقی"
        message = f"""
        سلام {user.username}،
        
        به وبسایت موسیقی خوش آمدید!
        لطفاً برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:
        
        {verification_link}
        
        اگر شما ثبت‌نام نکرده‌اید، این ایمیل را نادیده بگیرید.
        
        با تشکر،
        تیم پشتیبانی
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            email_status = "ایمیل تایید ارسال شد"
        except Exception as e:
            print(f"خطا در ارسال ایمیل: {e}")
            email_status = "خطا در ارسال ایمیل"
        
        return Response({
            "message": "کاربر با موفقیت ثبت‌نام شد. لطفاً ایمیل خود را تایید کنید.",
            "email_status": email_status,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="logined succesfuly",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: "auth error",
        }
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # جستجو با username یا email
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return Response(
                {"error": "نام کاربری یا رمز عبور اشتباه است."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.check_password(password):
            return Response(
                {"error": "نام کاربری یا رمز عبور اشتباه است."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.email_verified:
            return Response(
                {"error": "لطفاً ابتدا ایمیل خود را تایید کنید."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # ایجاد توکن JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="توکن تایید ایمیل",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={200: "ایمیل تایید شد"}
    )

    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {"error": "توکن یافت نشد."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email_verification_token=token)
            
            if user.email_verified:
                return Response({"message": "ایمیل قبلاً تایید شده است."})
            
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            
            return Response({"message": "ایمیل با موفقیت تایید شد. اکنون می‌توانید وارد شوید."})
            
        except User.DoesNotExist:
            return Response(
                {"error": "توکن نامعتبر است."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={200: "خروج موفق"}
    )

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "با موفقیت خارج شدید."})
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
# File upload      
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)   # برای دریافت فایل
    permission_classes = [IsAuthenticated]           # حتماً کاربر لاگین کرده باشه

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        style = request.data.get('style')
        instrument = request.data.get('instrument')

        if not uploaded_file:
            return Response({"error": "فایلی انتخاب نشده."}, status=400)

        # (اختیاری) اینجا می‌تونی فایل رو ذخیره کنی
        # فعلاً فقط یه پیغام موفقیت برمی‌گردونیم
        return Response({
            "message": f"فایل '{uploaded_file.name}' با موفقیت آپلود شد.",
            "style": style,
            "instrument": instrument
        }, status=200)
#email verification    
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from .models import PendingRegistration

class InitiateRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=InitiateRegistrationSerializer)
    def post(self, request):
        serializer = InitiateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # چک تکراری نبودن ایمیل / نام کاربری
        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "این ایمیل قبلاً ثبت شده است."}, status=400)
        if User.objects.filter(username=data['username']).exists():
            return Response({"error": "این نام کاربری قبلاً انتخاب شده."}, status=400)

        # ساخت کد ۶ رقمی
        code = ''.join(random.choices(string.digits, k=6))

        # ذخیرهٔ موقت
        pending = PendingRegistration.objects.create(
            first_name=data['first_name'],
            last_name=data.get('last_name', ''),
            email=data['email'],
            username=data['username'],
            password=data['password'],  # بعداً هش می‌شود
            fav_genre=data.get('fav_genre', ''),
            main_instrument=data.get('main_instrument', ''),
            verification_code=code
        )

        # ارسال ایمیل
        subject = "کد تأیید ثبت‌نام در فورته پیانو"
        message = f"کد تأیید شما: {code}"
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [data['email']], fail_silently=False)
        except Exception as e:
            print(f"خطا در ارسال ایمیل: {e}")
            # در محیط توسعه با console backend، کد توی ترمینال چاپ می‌شود

        return Response({"message": "کد تأیید به ایمیل شما ارسال شد."}, status=200)


class VerifyRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=VerifyRegistrationSerializer)
    def post(self, request):
        serializer = VerifyRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            pending = PendingRegistration.objects.get(email=email, verification_code=code)
        except PendingRegistration.DoesNotExist:
            return Response({"error": "کد نامعتبر است."}, status=400)

        # چک زمان انقضا (اختیاری، مثلاً ۱۰ دقیقه)
        if (timezone.now() - pending.created_at).seconds > 600:
            pending.delete()
            return Response({"error": "کد منقضی شده است."}, status=400)
        pending.email_verified = True
        pending.save()

        return Response({
            "message": "ایمیل شما تأیید شد. "
        }, status=200)

class CompleteRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=CompleteRegistrationSerializer)
    def post(self, request):
        serializer = CompleteRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        fav_genre = serializer.validated_data.get('fav_genre', '')
        main_instrument = serializer.validated_data.get('main_instrument', '')

        try:
            pending = PendingRegistration.objects.get(email=email, email_verified=True)
        except PendingRegistration.DoesNotExist:
            return Response({"error": "ایمیل تأیید نشده یا اطلاعات موقت یافت نشد."}, status=400)

        # چک تکراری نبودن نام کاربری
        if User.objects.filter(username=username).exists():
            return Response({"error": "این نام کاربری قبلاً انتخاب شده است."}, status=400)

        # ساخت کاربر نهایی
        user = User.objects.create_user(
            username=username,
            email=pending.email,
            password=pending.password,
            first_name=pending.first_name,
            last_name=pending.last_name,
            fav_genre=fav_genre,
            main_instrument=main_instrument,
            email_verified=True,
            is_active=True
        )

        pending.delete()
        return Response({"message": "ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید."}, status=201)     