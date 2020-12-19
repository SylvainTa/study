from celery import Celery

app = Celery('sgyp', broker='redis://@127.0.0.1:6379/1', backend='redis://@127.0.0.1:6379/2')

# 任务函数
@app.task
def task_test(a,b):
    print('-task is running-')
    return a+b