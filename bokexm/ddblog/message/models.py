from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import UserProfile


class Message(models.Model):
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    parent_message = models.IntegerField(default=0)