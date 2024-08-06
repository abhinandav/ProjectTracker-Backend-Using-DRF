
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('user.urls')),
    # path('auth/', include('social_django.urls', namespace='social')),
    # path('api-auth/', include('drf_social_oauth2.urls',namespace='drf')),
]
