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
from django.utils.decorators import method_decorator
from typing import Union
from PIL import Image
import uuid
from .utils import *
from .forms import *
from .models import *


class UserAccount(View):
    @method_decorator(login_required)
    def get(self, request):
        user = User.objects.get(username=request.user)
        return render(
            request, "blog/user_account.html", {"user": user, "title": f"user/{user}"}
        )

    @method_decorator(login_required)
    def post(self, request):
        upload_image = request.FILES.get("photo")
        if upload_image:
            image = Image.open(upload_image)
            image.thumbnail((200, 200))
            user_profile = User.objects.get(username=request.user)
            if user_profile.image:
                user_profile.image.delete()
            unique_image_name = (
                str(uuid.uuid4()) + upload_image.name[upload_image.name.rfind(".")]
            )
            user_profile.image.save(unique_image_name, upload_image)
        return redirect("user_account")


def post_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    dislike = Dislike.objects.filter(user=request.user, post=post)
    if not created:
        like.delete()
    if dislike:
        dislike.delete()

    return redirect("post", post_id)


def post_dislike(request, post_id):
    post = Post.objects.get(pk=post_id)
    dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
    like = Like.objects.filter(user=request.user, post=post)
    if not created:
        dislike.delete()
    if like:
        like.delete()
    return redirect("post", post_id)


class BlogPost(View):
    def get(self, request, postid: int) -> HttpResponse:
        post: Post = get_object_or_404(Post, pk=postid)
        comments: QuerySet[Comment] = Comment.objects.filter(post=post).order_by(
            "-created"
        )
        likes = Like.objects.filter(post=post).count()
        dislikes = Dislike.objects.filter(post=post).count()
        return render(
            request,
            "blog/post.html",
            {
                "post": post,
                "comments": comments,
                "user_auth": str(request.user),
                "likes": likes,
                "dislikes": dislikes,
            },
        )

    def post(self, request, postid: int) -> HttpResponse:
        user = str(request.user)
        user_comment = request.POST.get("comment", "")
        post: Post = get_object_or_404(Post, pk=postid)
        comment: Comment = Comment(
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
