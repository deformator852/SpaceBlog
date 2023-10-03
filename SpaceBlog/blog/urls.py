from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
from .views import *

urlpatterns = [
    path("spaceblog/", BlogPosts.as_view(), name="home"),
    path("login/", BlogLogin.as_view(), name="login"),
    path("registration/", BlogRegistration.as_view(), name="registration"),
    path("post/<int:postid>/", BlogPost.as_view(), name="post"),
    path(
        "confirm_email/",
        TemplateView.as_view(template_name="blog/confirm_email.html"),
        name="confirm_email",
    ),
    path("verify_email/<uidb64>/<token>/", EmailVerify.as_view(), name="verify_email"),
    path(
        "verify_email_error/",
        TemplateView.as_view(
            template_name="blog/user_validation_error.html",
        ),
        name="user_validation_error",
    ),
    path("post_like/<int:post_id>/", post_like, name="post_like"),
    path("post_dislike/<int:post_id>/", post_dislike, name="post_dislike"),
    path("user_account/",UserAccount.as_view(),name="user_account"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
