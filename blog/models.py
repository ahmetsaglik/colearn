from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings

from ckeditor.fields import RichTextField

def get_header_image_filepath(self, filename):
    return f'header_images/{self.pk}/{filename}'

class BlogPost(models.Model):
    title                   = models.CharField(max_length=50, null=False, blank=False)
    header_image            = models.ImageField(max_length=255, upload_to=get_header_image_filepath, null=True, blank=True)
    body                    = RichTextField(blank=True, null=True)
    tag                     = models.CharField(max_length=50)
    date_published          = models.DateTimeField(auto_now_add=True, verbose_name='date published')
    date_updated            = models.DateTimeField(auto_now=True, verbose_name='date updated')
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug                    = models.SlugField(blank=True, unique=True)
    likes                   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes_post', blank=True, null=True)
    unlikes                 = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='unlikes_post', blank=True, null=True)


    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

    def __str__(self):
        return self.title


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)

pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)


class Comment(models.Model):
    post                    = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_author', on_delete=models.CASCADE)
    body                    = models.TextField()
    date_added              = models.DateTimeField(auto_now_add=True)
    likes                   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes_comment', blank=True)
    unlikes                 = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='unlikes_comment', blank=True)


    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

    def __str__(self):
        return f"{self.post.title} - {self.author.username}"
    

class Notification(models.Model):
    ## 1-Like 2-Comment 3-Reply
    notification_type       = models.SmallIntegerField()
    to_user                 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user               = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post                    = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    comment                 = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    date                    = models.DateTimeField(default=timezone.now)
    user_has_seen           = models.BooleanField(default=False)
    



class Reply(models.Model):
    comment                     = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    user                        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reply                       = models.TextField(max_length=2000)
    timestamp                   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

    @property
    def get_replies(self):
        return self.replies.all()


class PostToAnotherPost(models.Model):
    slug                    = models.SlugField(blank=True, unique=True)
    title                   = models.CharField(max_length=50, null=False, blank=False)
    header_image            = models.ImageField(max_length=255, upload_to=get_header_image_filepath, null=True, blank=True)
    body                    = RichTextField(blank=True, null=True)
    tag                     = models.CharField(max_length=50)
    date_published          = models.DateTimeField(auto_now_add=True, verbose_name='date published')
    date_updated            = models.DateTimeField(auto_now=True, verbose_name='date updated')
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes                   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', blank=True, null=True)
    unlikes                 = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='unlikes', blank=True, null=True)
    post_to_post            = models.ForeignKey(BlogPost, related_name='reply_post', null=True, blank=True, on_delete=models.CASCADE)


    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

    def __str__(self):
        return self.title


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)

pre_save.connect(pre_save_blog_post_receiver, sender=PostToAnotherPost)








