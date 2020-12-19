from celery import Celery

# 1 创建Celery对象

app = Celery('tedu', broker='redis://@127.0.0.1:6379/1')


# 2 编写任务函数（比较耗时操作）

@app.task
def task_test():
   print('-task is running!-')