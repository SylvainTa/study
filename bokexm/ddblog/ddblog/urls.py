"""ddblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from ddblog import views
from ddblog.user import views as user_views
from btoken import views as btoken_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 返回测试页面
    path('test_cors', views.test_cors),
    # 跨域get请求
    path('test_cors_server', views.test_cors_server),
    #     用户url的处理
    #     1.处理方式1
    #     当多一个资源有多个请求方式时，这种基于视图函数的方式不合时宜了（FBV）
    # path('v1/users',)
    #     2.一个资源有多个请求方式，使用视图类（CBV）
    #     可以让视图类的请求方法与请求方式相对应.
    path('v1/users', user_views.UserView.as_view()),
    path('v1/users/', include('user.urls')),
    path('v1/tokens', btoken_views.TokenView.as_view()),
    path('v1/topics/', include('topic.urls')),
    path('v1/messages/', include('message.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
