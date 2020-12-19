from celery import Celery
from django.conf import settings
import os

# 添加环境变量，告诉celery为我们当前的ddblog项目服务
os.environ.setdefault("DJANGO_SETTINGS_MODULE","ddblog.settings")

# 创建celery对象
app = Celery('ddblog')

# 配置 celery
app.conf.update(
    BROKER_URL = 'redis://@127.0.0.1:6379/1'
)

# 告诉Celery去哪些应用下找任务资源
app.autodiscover_tasks(settings.INSTALLED_APPS)
