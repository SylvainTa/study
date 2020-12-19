import random

from django.db import models


def default_sign():
    signs = ['秃头老年人', '好吃小宝贝', '神秘组织成员', '夜店小王子']
    return random.choice(signs)


# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=20, verbose_name='用户名', primary_key=True)
    nickname = models.CharField(max_length=20, verbose_name='昵称',default='')
    # 如何生成一个随机的个人签名的默认值
    sign = models.CharField(max_length=50, verbose_name='个人签名', default=default_sign)
    email = models.EmailField(verbose_name='邮箱')
    password = models.CharField(max_length=32)
    info = models.CharField(max_length=150, verbose_name='个人简介', default='')
    avatar = models.ImageField(upload_to='avatar', null=True, verbose_name='头像')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, default='')

    class Meta:
        db_table = 'user_user_profile'
