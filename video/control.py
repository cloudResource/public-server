import os
import time
import json
import requests, re


def start_recording(domain, mac_address):
    """
    开始录制视频
    :mac_address: 设备MAC地址
    :return:
    """
    url = domain + "/control/v1/video_start"
    data = {"mac_address": mac_address}
    res = requests.post(url, data=data)
    response_data = res.json()
    return response_data



def stop_recording(domain, mac_address):
    """
    结束录制视频
    :domain: 学校域名
    :mac_address: 设备MAC地址
    :return:
    """
    url = domain + "/control/v1/video_stop"
    data = {"mac_address": mac_address}
    res = requests.post(url, data=json.dumps(data))
    response_data = res.json()
    return response_data


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
