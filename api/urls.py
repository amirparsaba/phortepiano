from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (FileUploadView, InitiateRegistrationView, VerifyRegistrationView, 
                    CompleteRegistrationView, MusicSheetListCreate, MusicSheetRetrieveUpdateDestroy, 
                    SheetPageView, CommentListCreate, SheetPageCountView, UserSheetsView)

urlpatterns = [
    path("users/", views.UserListCreate.as_view(), name="user-view-create"),
    path(
        "users/<int:pk>/",
        views.UserRetrieveUpdateDestroy.as_view(),
        name="user-update"
    ),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path('upload/', FileUploadView.as_view(), name='upload-file'),
    path('initiate-register/', InitiateRegistrationView.as_view(), name='initiate-register'),
    path('verify-registration/', VerifyRegistrationView.as_view(), name='verify-registration'),
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete-registration'),
    path('sheets/', MusicSheetListCreate.as_view(), name='sheet-list-create'),
    path('sheets/<int:pk>/', MusicSheetRetrieveUpdateDestroy.as_view(), name='sheet-detail'),
    path('sheets/<int:pk>/page/<int:page_num>/', SheetPageView.as_view(), name='sheet-page'),
    path('sheets/<int:sheet_id>/comments/', CommentListCreate.as_view(), name='sheet-comments'),
    path('sheets/<int:pk>/page_count/', SheetPageCountView.as_view(), name='sheet-page-count'),
    path('my-sheets/', UserSheetsView.as_view(), name='my-sheets'),
]
