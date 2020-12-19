from tools.logging_dec import get_user_by_request
from django.core.cache import cache


def topic_cache(expire):
    def _topic_cache(func):
        def wrapper(request, *args, **kwargs):
            # 只缓存博客列表暂时不考虑详情页的缓存
            if 't_id' in request.GET.keys():
                # 详情页
                return func(request, *args, **kwargs)
            # 博客列表页，需要加和缓存
            visitor = get_user_by_request(request)
            author_id = kwargs['author_id']
            print("visitor is %s  author is %s" % (visitor, author_id))
            if visitor == author_id:
                cache_key = 'topic_cache_self_%s' % (request.get_full_path())
            else:
                cache_key = 'topic_cache_%s' % (request.get_full_path())
            print('-cache is %s-' % cache_key)
            # 下面体现的是缓存思想
            res = cache.get(cache_key)
            if res:
                print('------------cache in-----------')
                return res
            res = func(request,*args,**kwargs)
            cache.set(cache_key,res,expire)
            return res


        return wrapper

    return _topic_cache
