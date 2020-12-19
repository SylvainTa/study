import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


# Create your views here.
# 1、 登录验证的装饰器
from message.models import Message
from tools.logging_dec import logging_check
from topic.models import Topic


@logging_check
def message_view(request, topic_id):
    # 2、 验证只能是post提交
    if request.method != 'POST':
        result = {'code':10402,'error':'请求方式不是POST'}
        # print(result)
        return JsonResponse(result)
    # 3、获取数据 content  parent_id
    # json_obj.get('parent_id',0)
    json_str = request.body
    json_obj = json.loads(json_str)
    parent_id = json_obj.get('parent_id',0)
    content = json_obj['content']

    # 4、根据topic_id 验证有无这篇文章
    try:
        topic = Topic.objects.get(id = topic_id)
    except Exception as e:
        result = {'code': 10405, 'error': '文章id错误'}
        # print(result)
        return JsonResponse(result)
    # if parent_id != topic_id:
    #     result = {'code': 10403, 'error': '查询不到该文章'}
    #     print(result)
    #     return JsonResponse(result)
    # 5、从request.user 获取用户
    user = request.myuser
    Message.objects.create(topic=topic,parent_message=parent_id,content=content,user_profile = user)

    # 6、添加到数据库（使用mysql查询是否插入成功）

    return JsonResponse({'code': 200})
