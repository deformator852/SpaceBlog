from django.shortcuts import render, redirect
from django.views.generic import View, CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import *
from .models import *


class BlogPost(View):
    def get(self, request, postid):
        post = get_object_or_404(Post, pk=postid)
        comments = Comments.objects.filter(post=post)
        return render(request, 'blog/post.html', {'post': post, 'comments': comments, 'user_auth': str(request.user)})

    def post(self, request, postid):
        user = str(request.user)
        user_comment = request.POST.get('comment', '')
        post = get_object_or_404(Post, pk=postid)
        comment = Comments(post=post, author_comment=user,
                           comment=user_comment, created=timezone.now())
        comment.save()

        return redirect('post', postid)


class BlogHome(View):
    def get(self, request):
        return render(request, 'blog/index.html')


class BlogPosts(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'blog/posts.html', {'posts': posts})


class BlogLogin(LoginView):
    form_class = LoginUserForm
    template_name = 'blog/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


class BlogRegistration(CreateView):
    form_class = RegisterUserForm
    template_name = 'blog/registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'User with this email already exist')
            return self.form_invalid(form)
        else:
            response = super().form_valid(form)
            self.object.message = 'Registration successful!Confirm your email!'
            return response
