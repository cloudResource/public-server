from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from public_server.settings import PAGINATOR

# 分页功能
def data_paginator(obj, page, limit):
    """
    :param obj: 列表、元组或其它可迭代的对象
    :param page: 第几页
    :param limit: 每页的数量
    :return: obj
    """
    page = page if page else PAGINATOR.get("current_page")
    limit = limit if limit else PAGINATOR.get("limit")
    paginator = Paginator(obj, limit)
    try:
        obj = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        obj = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        # obj = paginator.page(paginator.num_pages)
        obj = list()
    return obj

if __name__ == '__main__':
    obj_iterable = data_paginator(['john','paul','george','ringo','lucy','meir','che','wind','flow','rain'], 1, 3)
    print(obj_iterable.object_list)
    print(type(obj_iterable))
