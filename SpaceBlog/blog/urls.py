from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from .views import *

urlpatterns = [
    path('spaceblog/', BlogPosts.as_view(), name='home'),
    path('login/', BlogLogin.as_view(), name='login'),
    path('registration/', BlogRegistration.as_view(), name='registration'),
    path('post/<int:postid>/', BlogPost.as_view(), name='post')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
