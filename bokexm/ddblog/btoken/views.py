import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from user.models import UserProfile
import hashlib
from user.views import make_token


class TokenView(View):
    def get(self, request):
        return HttpResponse('-btoken get-')

    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        password = json_obj['password']
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            print('-%s-' % e)
            result = {'code': 10200, 'error': '错误'}
            return JsonResponse(result)
        md5 = hashlib.md5()
        md5.update(password.encode())
        if md5.hexdigest() != user.password:
            result = {'code': 10200, 'error': '错误'}
            return JsonResponse(result)
        # 校验成功后，生成token
        token = make_token(username)

        result = {'code': 200, 'username': username, 'password': password,
                  'data': {'token': token.decode()}}

        return JsonResponse(result)
