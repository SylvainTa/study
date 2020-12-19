from django.db import models
from user.models import UserProfile


# Create your models here.
class Topic(models.Model):
    title = models.CharField('标题', max_length=50)
    category = models.CharField('文章分类', max_length=20)
    limit = models.CharField('权限', max_length=20)
    introduce = models.CharField('简介', max_length=90)
    content = models.TextField('文章内容')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
