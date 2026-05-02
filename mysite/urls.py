from django.contrib import admin #admin url
from django.urls import path, include
from rest_framework import permissions #for swagger url
from drf_yasg.views import get_schema_view #swagger
from drf_yasg import openapi #swagger
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title='forte piano API',
        default_version='v1',
        description="you can test all API here",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="bqayyamyrparsa@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger urls :
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    path('', include("api.urls") ),
    
]
# Profile pic url and root
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)