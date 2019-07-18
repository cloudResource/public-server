from celery import Celery, platforms

# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'public_server.settings'

# 创建celery应用
celery_app = Celery('writingsys')

# 导入celery配置
celery_app.config_from_object('celery_tasks.config')
platforms.C_FORCE_ROOT = True

# 自动注册celery任务
celery_app.autodiscover_tasks(["celery_tasks.sms"], ["celery_tasks.video"])
