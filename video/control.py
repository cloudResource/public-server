import os
import re
import time

import requests, re
from xml.etree import ElementTree


# 获取状态
def get_status():
    url = "http://192.168.2.235"
    payload = {"custom": 1, "cmd": 3014}
    res = requests.get(url, payload)
    res.encoding = 'utf-8'
    ipaddress = res.text
    return ipaddress


# 获取文件列表
def get_files():
    file_list = []
    url = "http://192.168.2.235"
    payload = {"custom": 1, "cmd": 3015}
    try:
        res = requests.get(url, payload)
        res.encoding = 'utf-8'
        root = ElementTree.XML(res.text)  # 将字符串解析为XML
        for node in root.iter("File"):  # 迭代寻找TrainDetailInfo标签
            # print(node.tag,node.attrib) #node的标签和属性
            fpath = node.find('FPATH').text  # 寻找node下的标签
            pat = r'.*DCIM.*Video'
            ret = re.findall(pat, fpath)
            if ret:
                name = node.find('NAME').text
                size = node.find('SIZE').text
                time = node.find('TIME').text
                timecode = node.find('TIMECODE').text
                file_list.append({"name": name,
                                  "fpath": fpath,
                                  "size": size,
                                  "time": time,
                                  "timecode": timecode})
        return file_list
    except:
        return False


def del_all_files():
    """
    删除所有文件
    :return:
    """
    url = "http://192.168.2.235"
    payload = {"custom": 1, "cmd": 4004}
    try:
        res = requests.get(url, payload)
        res.encoding = 'utf-8'
        return True
    except:
        return False


def switch_state(par):
    """
    切换模式
    :par: 1录像模式，2回看模式
    :return:
    """
    url = "http://192.168.2.235"
    payload = {"custom": 1, "cmd": 3001, "par": par}
    try:
        res = requests.get(url, payload)
        res.encoding = 'utf-8'
        return True
    except:
        return False


# 录制视频
def video_recording(par):
    """
    :par: 1开始录制，0停止录制
    :return:
    """
    url = "http://192.168.2.235"
    payload = {"custom": 1, "cmd": 2001, "par": par}
    try:
        res = requests.get(url, payload)
        res.encoding = 'utf-8'
        return True
    except:
        return False


def unix_time(dt):
    """
    日期转时间戳
    """
    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y/%m/%d %H:%M:%S")
    # 转换成时间戳
    timestamp = int(time.mktime(timeArray))
    return timestamp


def custom_time(timestamp):
    """
    时间戳转日期
    """
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data
