from django.http import JsonResponse


def check_login(action):
    """
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

