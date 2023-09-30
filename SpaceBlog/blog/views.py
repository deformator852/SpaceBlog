from django.shortcuts import render, redirect
from django.views.generic import View, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import QuerySet
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import AbstractBaseUser
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
        return reverse_lazy("home")


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
            user: Union[User,None] = authenticate( #pyright: ignore
                email=email, username=username, password=password
            )
            send_email_for_verify(request, user) #pyright: ignore
            return redirect("confirm_email")

        return render(request, "blog/registration.html", {"form": form})


class EmailVerify(View):
    pass
