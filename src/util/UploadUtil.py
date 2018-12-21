# -*- coding:utf-8 -*-
# coding:utf-8

import os
from io import BytesIO
import configparser
import requests
import hashlib

import oss2

__author__ = 'zxk175'
__date__ = '2018/12/20'

cf = configparser.ConfigParser()
cf.read("./conf/conf.ini")

env = "oss"

AccessKeyId = cf.get(env, 'AccessKeyId')
AccessKeySecret = cf.get(env, 'AccessKeySecret')
Endpoint = cf.get(env, 'Endpoint')
Bucket = cf.get(env, 'Bucket')

# 输入AccessKeyId和AccessKeySecret
auth = oss2.Auth(AccessKeyId, AccessKeySecret)
# 输入Endpoint和Bucket名
bucket = oss2.Bucket(auth, Endpoint, Bucket)


def get_file_md5(result, ext):
    byte = BytesIO(result.content)
    md5 = hashlib.md5(byte.read()).hexdigest()
    return md5 + ext


def get_file_ext_name(path):
    return os.path.splitext(path)[1]


class UploadOss:
    def __init__(self, oss_path, http_url):
        self.ossPath = oss_path
        self.httpUrl = http_url
        self.ossImgUrl = ""

    def get_oss_path(self, md5):
        path = self.ossPath + "/" + md5
        self.ossImgUrl = path
        return path

    def download(self, url, retry_time):
        input = requests.get(url)
        if input.status_code == 200:
            return input
        if retry_time < 3:
            self.download(url, retry_time + 1)
        return

    def upload(self, input, retry_time):
        ext = get_file_ext_name(self.httpUrl)
        md5 = get_file_md5(input, ext)
        result = bucket.put_object(self.get_oss_path(md5), input)
        if result.status == 200:
            return result
        if retry_time < 3:
            self.upload(input, retry_time + 1)

    def upload_oss(self):
        # 上传文件
        input = self.download(self.httpUrl, 3)
        result = self.upload(input, 3)

        # 判断上传成功
        if 200 == result.status:
            print("上传成功")
        else:
            print("上传失败")
            return

        return 'http://oss-test.szsdyc.cn/' + self.ossImgUrl
