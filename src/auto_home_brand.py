# -*- coding:utf-8 -*-
# coding:utf-8

import requests
from bs4 import BeautifulSoup

from src.util.UploadUtil import UploadOss
from src.util import DbUtil

__author__ = 'zxk175'
__date__ = '2018/12/20'

CAR_BRAND_URL = 'https://car.m.autohome.com.cn/'

HEADERS = {
    'Accept': 'text/html, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN; q=0.5',
    'Connection': 'Keep-Alive',
    'Host': 'zhannei.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}


def get_brand():
    car_brand = requests.get(CAR_BRAND_URL)
    car_brand.headers = HEADERS
    car_brand.encoding = "utf-8"
    if 200 == car_brand.status_code:
        soup = BeautifulSoup(car_brand.text, "html.parser")
        brand_list = soup.select('.anchor')
        brand_box_list = soup.select('ul')

        for i in range(len(brand_list)):
            first_letter = brand_list[i].get('data-tips')
            car_list = brand_box_list[i].select("li")

            for j in range(len(car_list)):
                li = car_list[j]
                item = li.select(".item")

                brand_id = li.get("v")
                brand_name = item[0].select("span")[0].string

                logo = item[0].select("img")[0]
                logo_url = logo.get("src")

                if logo_url is None:
                    logo_url = logo.get("data-src")

                args = (DbUtil.get_id(), brand_name, first_letter, logo_url, brand_id)
                add_brand(args)


def add_brand(args):
    print(args[4])
    third_id = DbUtil.execute("SELECT third_id FROM t_car_brand WHERE `status` = 1 AND third_id = " + args[4])

    if 0 == third_id.__len__():
        # 图片上传Oss
        oss_path = "car/brand/logo/" + args[2].lower()
        upload = UploadOss(oss_path, 'http:' + args[3])
        oss_img_url = upload.upload_oss()

        db_args = []
        sub_args = (args[0], args[1], oss_img_url, args[2], args[4])
        db_args.append(sub_args)

        sql = "INSERT INTO t_car_brand(`brand_id`, `brand_name`, `brand_logo`, `first_letter`, `third_id`, `create_time`) VALUES(%s, %s, %s, %s, %s, now())"
        DbUtil.execute_insert(sql, db_args)


if '__main__' == __name__:
    print("开始抓取车品牌数据...\n")
    get_brand()
