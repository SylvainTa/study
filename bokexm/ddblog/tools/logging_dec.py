import jwt
from django.http import JsonResponse

from django.conf import settings

from user.models import UserProfile


def logging_check(func):
    def wrap(request, *args, **kwargs):
        # 从请求头中获取token
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code': 403, 'error': 'please login'}
            return JsonResponse(result)
        # 校验token
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY)
        except Exception as e:
            print(" error is %s" % e)
            result = {'code': 10403, 'error': 'please login'}
            return JsonResponse(result)
        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user
        return func(request, *args, **kwargs)

    return wrap

def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res = jwt.decode(token,settings.JWT_TOKEN_KEY)
    except Exception as e :
        print('error is %s'%e)
        return None
    username = res['username']
    return username


