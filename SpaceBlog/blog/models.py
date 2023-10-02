from django.db import models
from django.contrib.auth.models import AbstractUser


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    images = models.ImageField(upload_to="photos/%Y/%m/%d/", null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    author_comment = models.CharField(max_length=255)
    comment = models.CharField(max_length=1200)
    created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.author_comment

class User(AbstractUser):
    email_verify = models.BooleanField(default=False, unique=True)


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)


class Dislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


