import os
from ctypes import *

if __name__ == '__main__':

    d = os.path.dirname(__file__)
    cur = cdll.LoadLibrary(d + '/videocv.so')
    get_video = cur.Video
    free = cur.Free
    try:
        # get_cover.restype = c_char
        # get_cover.argtypes = [POINTER(c_char), c_char_p]
        # get_cover.argtypes = c_char
        # ret = cur.GetCover("/dev/shm/videos/20190715_112204A.MP4/20190715_112204A.MP4", c_char_p)
        r = get_video("/dev/shm/videos/20190716_111756A.TS/h264_20190716_111756A.MP4".encode())
    except Exception as e:
        pass


