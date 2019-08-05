from django.http import JsonResponse

from user.models import User


def check_login(action):
    """
    学校管理员PC端
    校验用户状态装饰器

    """

    def check_data(func):
        def wrapped(request, *args, **kwargs):
            user_id = request.session.get('user_id')
            role = request.session.get('role')
            if not user_id:
                return JsonResponse(data={"error": "登录过期", "status": 401})
            if role != "admin":
                return JsonResponse(data={"error": "您无权操作", "status": 400})

            return func(request, *args, **kwargs)

        return wrapped

    return check_data


def check_token(action):
    """
    微信小程序校验用户是否注册

    """

    def check_data(func):
        def wrapped(request, *args, **kwargs):
            token = request.META.get("HTTP_TOKEN", None)
            if not token:
                return JsonResponse(data={"error": "缺少token信息", "status": 400})

            return func(request, token, *args, **kwargs)

        return wrapped

    return check_data
