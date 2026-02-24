from django.urls import path
from . import views

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
    )
]
