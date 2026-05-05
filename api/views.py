from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
import fitz
import random
import string

from .models import User, MusicSheet, Comment, PendingRegistration
from .serializers import (
    UserSerializer, LoginSerializer, MusicSheetSerializer,
    CommentSerializer, InitiateRegistrationSerializer,
    VerifyRegistrationSerializer, CompleteRegistrationSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# ==================== User Management ====================
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class UserList(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'username', openapi.IN_QUERY,
                description="جستجوی کاربر بر اساس نام کاربری",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, format=None):
        username = request.query_params.get("username", "")
        if username:
            users = User.objects.filter(username__icontains=username)
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== File Upload ====================
class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        style = request.data.get('style')
        instrument = request.data.get('instrument')

        if not uploaded_file:
            return Response({"error": "فایلی انتخاب نشده."}, status=400)

        return Response({
            "message": f"فایل '{uploaded_file.name}' با موفقیت آپلود شد.",
            "style": style,
            "instrument": instrument
        }, status=200)


# ==================== User Profile ====================
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        return self.request.user


# ==================== User Sheets ====================
class UserSheetsView(generics.ListAPIView):
    serializer_class = MusicSheetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MusicSheet.objects.filter(author=self.request.user).order_by('-published_date')


# ==================== Authentication ====================
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="ورود موفق",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            401: "خطای احراز هویت",
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return Response({"error": "نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"error": "نام کاربری یا رمز عبور اشتباه است."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.email_verified:
            return Response({"error": "لطفاً ابتدا ایمیل خود را تایید کنید."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')},
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
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== Registration with OTP ====================
class InitiateRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=InitiateRegistrationSerializer)
    def post(self, request):
        serializer = InitiateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data['email']).exists():
            return Response({"error": "این ایمیل قبلاً ثبت شده است."}, status=400)

        code = ''.join(random.choices(string.digits, k=6))

        PendingRegistration.objects.create(
            first_name=data['first_name'],
            last_name=data.get('last_name', ''),
            email=data['email'],
            username='',
            password=data['password'],
            fav_genre='',
            main_instrument='',
            verification_code=code
        )

        subject = "کد تأیید ثبت‌نام در فورته پیانو"
        message = f"کد تأیید شما: {code}"
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [data['email']], fail_silently=False)
        except Exception as e:
            print(f"خطا در ارسال ایمیل: {e}")

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

        if (timezone.now() - pending.created_at).seconds > 600:
            pending.delete()
            return Response({"error": "کد منقضی شده است."}, status=400)

        pending.email_verified = True
        pending.save()

        return Response({"message": "ایمیل شما با موفقیت تأیید شد. اکنون نام کاربری و تنظیمات خود را تکمیل کنید."}, status=200)


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

        if User.objects.filter(username=username).exists():
            return Response({"error": "این نام کاربری قبلاً انتخاب شده است."}, status=400)

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


# ==================== Music Sheet ====================
class MusicSheetListCreate(generics.ListCreateAPIView):
    queryset = MusicSheet.objects.all().order_by('-published_date')
    serializer_class = MusicSheetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_create(self, serializer):
        sheet = serializer.save(author=self.request.user)
        if sheet.attachment:
            size_bytes = sheet.attachment.size
            if size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} کیلوبایت"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} مگابایت"
            sheet.file_size = size_str
            sheet.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.query_params.get('genre')
        search = self.request.query_params.get('search')

        if genre:
            queryset = queryset.filter(genre__iexact=genre)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(composer__icontains=search) |
                Q(arranger__icontains=search) |
                Q(tags__icontains=search)
            )
        return queryset


class MusicSheetRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = MusicSheet.objects.all()
    serializer_class = MusicSheetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ==================== PDF Pages ====================
class SheetPageView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, page_num):
        sheet = get_object_or_404(MusicSheet, pk=pk)
        if not sheet.attachment:
            return Response({"error": "No attachment"}, status=404)

        file_path = sheet.attachment.path
        if not file_path.lower().endswith('.pdf'):
            return Response({"error": "Attachment is not a PDF"}, status=400)

        try:
            doc = fitz.open(file_path)
            if page_num < 1 or page_num > doc.page_count:
                return Response({"error": "Page number out of range"}, status=400)

            page = doc.load_page(page_num - 1)
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            doc.close()
            return HttpResponse(img_bytes, content_type="image/png")
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SheetPageCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        sheet = get_object_or_404(MusicSheet, pk=pk)
        if not sheet.attachment or not sheet.attachment.name.lower().endswith('.pdf'):
            return Response({"page_count": 0})
        try:
            doc = fitz.open(sheet.attachment.path)
            count = doc.page_count
            doc.close()
            return Response({"page_count": count})
        except:
            return Response({"page_count": 0})


# ==================== Comments ====================
class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        sheet_id = self.kwargs['sheet_id']
        return Comment.objects.filter(sheet_id=sheet_id).order_by('-created_at')

    def perform_create(self, serializer):
        sheet = get_object_or_404(MusicSheet, pk=self.kwargs['sheet_id'])
        serializer.save(author=self.request.user, sheet=sheet)