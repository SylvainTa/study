from django.urls import path

from ddblog.user import views

urlpatterns = [
    #http://127.0.0.1:8000/v1/users/sms
    path('sms',views.sms_view),
    # http:127.0.0.1:8000/v1/users/username
    path('<str:username>',views.UserView.as_view()),
    path('<str:username>/avatar',views.user_avatar),
]