import json

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.cache import cache_page

from message.models import Message
from tools.cache_dec import topic_cache
from tools.logging_dec import logging_check, get_user_by_request
from django.utils.decorators import method_decorator

from user.models import UserProfile
from .models import Topic


class TopicViews(View):

    def make_topic_res(self, author, author_topic, is_self):
        # 上一篇/下一篇
        if is_self:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, user_profile_id=author.username).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, user_profile_id=author.username).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, user_profile_id=author.username,
                                              limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, user_profile_id=author.username,
                                              limit='public').last()
        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None

        # 获取所有的评论和回复信息
        all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list = []
        r_dict = {}
        for msg in all_messages:
            if msg.parent_message:
                #         回复
                r_dict.setdefault(msg.parent_message, [])
                r_dict[msg.parent_message].append({
                    'msg_id': msg.id,
                    'content': msg.content,
                    'publisher': msg.user_profile.nickname,
                    'publisher_avatar': str(msg.user_profile.avatar),
                    'created_time': msg.created_time.strftime('%Y/%m/%d  %H:%M:%S')
                })
            else:
                msg_list.append({'id': msg.id,
                                 'content': msg.content,
                                 'publisher': msg.user_profile.nickname,
                                 'publisher_avatar': str(msg.user_profile.avatar),
                                 'created_time': msg.created_time.strftime('%Y/%m/%d  %H:%M:%S'),
                                 'reply': []
                                 })
            # 将评论回复关联
            for m in msg_list:
                if m['id'] in r_dict:
                    m['reply'] = r_dict[m['id']]

        result = {'code': 200, 'data': {}}
        result['data']['nickname'] = author.nickname
        result['data']['title'] = author_topic.title
        result['data']['category'] = author_topic.category
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nickname
        result['data']['created_time'] = author_topic.create_time.strftime('%Y/%m/%d  %H:%M:%S')

        result['data']['last_id'] = last_id
        result['data']['last_title'] = last_title
        result['data']['next_id'] = next_id
        result['data']['next_title'] = next_title

        result['data']['messages'] = msg_list
        result['data']['messages_count'] = 0

        # print(result)

        return result

    def make_topics_res(self, author, author_topics):
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['introduce'] = topic.introduce
            d['created_time'] = topic.create_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.username
            topics_res.append(d)
        res = {'code': 200, 'data': {}}
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    def clear_topic_caches(self, request):
        all_path = request.path_info
        all_path_p = ['topic_cache_self_', 'topic_cache_']
        all_keys = []
        for key_p in all_path_p:
            for key_h in ['', '?category=tec', 'category=no-tec']:
                all_keys.append(key_p + all_path + key_h)
        print(all_keys)
        cache.delete_many(all_keys)

    @method_decorator(logging_check)
    def post(self, request, author_id):
        author = request.myuser
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj['content']

        content_text = json_obj['content_text']
        introduce = content_text[:20]

        title = json_obj['title']

        limit = json_obj['limit']
        if limit not in ['public', 'private']:
            result = {'code': 10300, 'error': '权限错误'}
            return JsonResponse(result)
        category = json_obj['category']
        if category not in ['tec', 'no-tec']:
            result = {'code': 10301, 'error': '分类错误'}
            return JsonResponse(result)
        # 数据入库（添加一篇新文章）
        Topic.objects.create(title=title, content=content, limit=limit, category=category, introduce=introduce,
                             user_profile=author)
        self.clear_topic_caches(request)
        return JsonResponse({'code': 200, 'username': author.username})

    @method_decorator(topic_cache(60))
    def get(self, request, author_id):
        # v1/topics/tt
        # v1/topics/tt?category=tec/no-tec
        # 访问者与文章作者是否为同一人，根据结果判断是否返回private文章
        # 判断author_id是否存在
        # 1、判断author_id是否为文章作者

        try:
            author = UserProfile.objects.get(username=author_id)
            # print(author)
        except Exception as e:
            result = {'code': 10305, 'error': '用户名称有误'}
            return JsonResponse(result)
        # 2、获取访问者
        visitor = get_user_by_request(request)

        t_id = request.GET.get('t_id')
        # print(t_id)
        # 是否是博主自己访问
        is_self = False
        if t_id:
            #     详情页
            if visitor == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id, user_profile_id=author_id)
                    print(author_topic)
                except Exception as e:
                    result = {'code': 10310, 'error': '获取文章错误'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, user_profile_id=author_id, limit='public')
                except Exception as e:
                    result = {'code': 10310, 'error': '获取文章错误'}
                    return JsonResponse(result)
            # 将对象封装为前端需要的json格式
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            # 列表页

            category = request.GET.get('category')
            filter_category = False
            if category in ['tec', 'no-tec']:
                filter_category = True

            if visitor == author_id:
                # 博主访问自己
                if filter_category:
                    # 是否需要分类
                    author_topics = Topic.objects.filter(user_profile_id=author_id, category=category)

                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id)
            else:
                # 他人访问，只显示public文章
                if filter_category:
                    # 是否需要分类
                    author_topics = Topic.objects.filter(user_profile_id=author_id, category=category, limit='public')

                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id, limit='public')
            # 讲Queryset，重新封装成前段需要的JSON格式
            res = self.make_topics_res(author, author_topics)
            # print(res)
            return JsonResponse(res)
