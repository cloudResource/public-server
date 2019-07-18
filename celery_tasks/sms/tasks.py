# 发送短信的异步任务
from .yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 装饰器将send_sms_code装饰为异步任务,并设置别名
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: None
    """

    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
