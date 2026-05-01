from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import FileUploadView, InitiateRegistrationView, VerifyRegistrationView, CompleteRegistrationView

urlpatterns = [
    path("blogposts/", views.BlogPostListCreate.as_view(), name="blogpost-view-create"),
    path(
        "blogposts/<int:pk>/", 
        views.BlogPostRetrieveUpdateDestroy.as_view(), 
        name="post-update",),
    path("users/", views.UserListCreate.as_view(), name="user-view-create"),
    path(
        "users/<int:pk>/",
        views.UserRetrieveUpdateDestroy.as_view(),
        name="user-update"
    ),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("verify-email/", views.EmailVerificationView.as_view(), name="verify-email"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path('upload/', FileUploadView.as_view(), name='upload-file'),
    path('initiate-register/', InitiateRegistrationView.as_view(), name='initiate-register'),
    path('verify-registration/', VerifyRegistrationView.as_view(), name='verify-registration'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete-registration')
]
