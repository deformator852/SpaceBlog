from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    images = models.ImageField(
        upload_to='photos/%Y/%m/%d/', null=True, blank=True)

    def __str__(self):
        return self.title


class Comments(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author_comment = models.CharField(max_length=255)
    comment = models.CharField(max_length=1200)
    created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.author_comment
