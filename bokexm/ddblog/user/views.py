import time

from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.views import View
import json
from user.tasks import send_sms
from tools.logging_dec import logging_check
from .models import UserProfile
import hashlib
# 在使用setting.py时，导入Django的模块
from django.conf import settings
from django.utils.decorators import method_decorator
import jwt
import random
from django.core.cache import cache
from tools.sms import YunTongXin


class UserView(View):
    def get(self, request, username=None):
        if username:
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                print('get user error %s') % e
                result = {'code': 10104, 'error': '错误'}
                return JsonResponse(result)
            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code': 200, 'username': username, 'data': data}
                return JsonResponse(result)

            else:
                result = {'code': 200, 'username': username,
                          'data': {'info': user.info, 'sign': user.sign, 'nickname': user.nickname,
                                   'avatar': str(user.avatar)}}
                return JsonResponse(result)

        return HttpResponse('-user get-')

    def post(self, request):
        # 1.获取ajax请求提交的数据
        json_str = request.body
        # 2. 将json串反序列化为对象
        json_obj = json.loads(json_str)
        print(json_obj)
        # 3.获取数据
        username = json_obj['username']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        email = json_obj['email']
        phone = json_obj['phone']

        #   获取验证码（查看前端页面是否传递验证码）
        sums_num = json_obj['sms_num']
        #   验证码检查
        #   1 从redis中获取并判断验证码是否为空
        cache_key = 'sms_%s' % phone
        sms_num = cache.get(cache_key)
        if not sums_num:
            result = {'code': 10107, 'error': '验证码为空！'}
            return JsonResponse(result)
        #   2 把接收的用户输入的验证码，与redis中的验证码比较
        #   两者不相等，直接返回
        if sms_num != int(sums_num):
            result = {'code': 10106, 'error': '验证码不正确！'}
            return JsonResponse(result)

        # 4.数据检查
        # 4.1 用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10100, 'error': '用户名已占用！'}
            return JsonResponse(result)
        # 4.2 两次密码是否一致
        if password_1 != password_2:
            result = {'code': 10101, 'error': '两次密码不一致！'}
            return JsonResponse(result)

        # 4.3 密码hash处理
        md5 = hashlib.md5()
        md5.update(password_1.encode())
        password_m = md5.hexdigest()

        # 5. 添加用户信息到数据库（需要做异常处理）
        try:
            user = UserProfile.objects.create(username=username, password=password_m, email=email, phone=phone,
                                              nickname=username)

        except Exception as e:
            print('create error is %s' % e)
            result = {'code': 10100, 'error': '用户名已被占用！'}
            return JsonResponse(result)
        token = make_token(username)

        return JsonResponse({'code': 200, 'username': username, 'data': {'token': token.decode()}})

    @method_decorator(logging_check)
    def put(self, request, username):
        # 拿数据
        json_str = request.body
        json_obj = json.loads(json_str)
        # 修改对象
        request.myuser.sign = json_obj['sign']
        request.myuser.nickname = json_obj['nickname']
        request.myuser.info = json_obj['info']
        # 保存到数据库
        request.myuser.save()
        #         返回
        result = {
            'code': 200,
            'username': request.myuser.username
        }
        return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'username': username, 'exp': now + expire}
    return jwt.encode(payload, key)


@logging_check
def user_avatar(request, username):
    if request.method != 'POST':
        result = {'code': 10105, 'error': '请使用POST请求'}
        return JsonResponse(result)
    user = request.myuser
    user.avatar = request.FILES['avatar']
    user.save()
    result = {'code': 200, 'username': user.username}
    return JsonResponse(result)


def sms_view(request):
    # 1.获取手机号
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']
    cache_key = 'sms_%s' % phone
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code': 10112, 'error': '没钱了，发不过去'}
        return JsonResponse(result)
    # 2.生成验证码
    code = random.randint(99999999, 99999999999)
    print('_________%s_________' % code)
    # 3.存储redis

    cache.set(cache_key, code, 65)
    # 将验证码发送到用户手机

    # x = YunTongXin(settings.SMS_ACCOUNT_ID, settings.SMS_ACCOUNT_TOKEN, settings.SMS_APP_ID, settings.SMS_TEMPLATE_ID)
    # res = x.run(phone, code)
    # print(res)

    # 异步发送（生产者）
    send_sms.delay(phone,code)

    return JsonResponse({'code': 200})
