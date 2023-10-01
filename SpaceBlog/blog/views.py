from django.shortcuts import render, redirect
from django.views.generic import View, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.db.models import QuerySet
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib import messages
from typing import Union
from .utils import *
from .forms import *
from .models import *


class BlogPost(View):
    def get(self, request, postid: int) -> HttpResponse:
        post: Post = get_object_or_404(Post, pk=postid)
        comments: QuerySet[Comments] = Comments.objects.filter(post=post)
        return render(
            request,
            "blog/post.html",
            {"post": post, "comments": comments, "user_auth": str(request.user)},
        )

    def post(self, request, postid: int) -> HttpResponse:
        user = str(request.user)
        user_comment = request.POST.get("comment", "")
        post: Post = get_object_or_404(Post, pk=postid)
        comment: Comments = Comments(
            post=post, author_comment=user, comment=user_comment, created=timezone.now()
        )
        comment.save()

        return redirect("post", postid)


class BlogHome(View):
    def get(self, request) -> HttpResponse:
        return render(request, "blog/index.html")


class BlogPosts(View):
    def get(self, request) -> HttpResponse:
        posts: QuerySet[Post] = Post.objects.all()
        return render(request, "blog/posts.html", {"posts": posts})


class BlogLogin(LoginView):
    form_class = LoginUserForm
    template_name = "blog/login.html"

    def get_success_url(self) -> HttpResponse:
        print("you log in!")
        return reverse_lazy("home")

    def form_valid(self, form):
        user = form.get_user()
        check_user = User.objects.get(username=user)
        if not check_user.email_verify == 1:
            print("Here")
            messages.error(self.request, "Your email not verify!")
            return super().form_invalid(form)

        return super().form_valid(form)


class BlogRegistration(View):
    def get(self, request) -> HttpResponse:
        form = RegisterUserForm()
        return render(request, "blog/registration.html", {"form": form})

    def post(self, request) -> HttpResponse:
        form: RegisterUserForm = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")
            user: Union[User, None] = authenticate(  # pyright: ignore
                email=email, password=password, username=username
            )
            send_email_for_verify(request, user)  # pyright: ignore
            return redirect("confirm_email")

        return render(request, "blog/registration.html", {"form": form})


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user: Union[User, None] = self.get_user(uidb64)
        if user is None and not token_generator.check_token(user, token):
            return redirect("user_validation_error")
        else:
            user.email_verify = True  # pyright: ignore
            user.save()  # pyright: ignore
            login(request, user)
            return redirect("home")

    def post(self, request):
        pass

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user
