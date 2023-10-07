from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from .models import User
from django.conf import settings
from SpaceBlog.celery import app

@app.task
def send_email_for_verify(username) -> None:
    current_site = Site.objects.get(id=settings.SITE_ID)
    user = User.objects.get(username=username)
    context = {
        "domain": current_site,
        "user": user,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": token_generator.make_token(user),
    }
    message = render_to_string("blog/verify_email.html", context=context)
    email = EmailMessage("Verify email", message, to=[user.email])
    email.send()
    print("email was send!")

