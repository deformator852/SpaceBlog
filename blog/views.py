from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.db.models import QuerySet
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.core.cache import cache
from django.conf import settings
from typing import Union
from PIL import Image
from .forms import *
from .models import *
from .tasks import *
import uuid


class AddNewPost(View):
    @method_decorator(login_required)
    def get(self, request) -> HttpResponse:  # pyright:ignore
        if request.user.is_staff:
            return render(request, "blog/add_new_post.html")

    @method_decorator(login_required)
    def post(self, request) -> HttpResponse:
        if request.user.is_staff:
            title = request.POST.get("title")
            content = request.POST.get("content")
            image = request.FILES.get("image")
            if image:
                new_post = Post(title=title, body=content, author=request.user,image=image)
                new_post.image = image
            else:
                new_post = Post(title=title, body=content, author=request.user)
            new_post.save()
        return redirect("user_account")


class UserAccount(View):
    @method_decorator(login_required)
    def get(self, request) -> HttpResponse:
        user = User.objects.values("username", "email", "image", "is_staff").get(
            username=request.user
        )
        return render(
            request,
            "blog/user_account.html",
            {
                "user": user,
                "title": f"user/{user}",
                "request": request,
                "media": settings.MEDIA_URL,
            },
        )

    @method_decorator(login_required)
    def post(self, request) -> HttpResponse:
        upload_image = request.FILES.get("photo")
        if upload_image:
            image = Image.open(upload_image)
            image.thumbnail((200, 200))
            user_profile: User = User.objects.get(username=request.user)
            if user_profile.image:
                user_profile.image.delete()
            unique_image_name = (
                str(uuid.uuid4()) + upload_image.name[upload_image.name.rfind(".")]
            )
            user_profile.image.save(unique_image_name, upload_image)
        return redirect("user_account")


def post_like(request, post_id: int) -> HttpResponse:
    post: Post = Post.objects.get(pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    dislike: QuerySet[Dislike] = Dislike.objects.filter(user=request.user, post=post)
    if not created:
        like.delete()
    if dislike:
        dislike.delete()

    return redirect("post", post_id)


def post_dislike(request, post_id: int) -> HttpResponse:
    post: Post = Post.objects.get(pk=post_id)
    dislike, created = Dislike.objects.get_or_create(user=request.user, post=post)
    like: QuerySet[Like] = Like.objects.filter(user=request.user, post=post)
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
                "likes": likes,
                "dislikes": dislikes,
            },
        )

    def post(self, request, postid: int) -> HttpResponse:
        user = User.objects.get(username=request.user)
        user_comment = request.POST.get("comment", "")
        post: Post = get_object_or_404(Post, pk=postid)
        comment: Comment = Comment(
            post=post, author_comment=user, comment=user_comment, created=timezone.now()
        )
        comment.save()

        return redirect("post", postid)


class BlogPosts(View):
    def get(self, request) -> HttpResponse:
        posts = Post.objects.values(
            "title", "body", "created", "author", "image", "id"
        ).order_by("-id")
        paginator = Paginator(posts,10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        print(request.user)
        return render(
                request, "blog/posts.html", {"posts": page_obj, "media": settings.MEDIA_URL,"user_auth":str(request.user)}
        )


class BlogLogin(LoginView):
    form_class = LoginUserForm
    template_name = "blog/login.html"

    def get_success_url(self) -> HttpResponse:
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
            send_email_for_verify.delay(username)
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
