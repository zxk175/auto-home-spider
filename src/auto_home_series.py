# -*- coding:utf-8 -*-
# coding:utf-8

import requests
from src.util.UploadUtil import UploadOss
from src.util import DbUtil

__author__ = 'zxk175'
__date__ = '2018/12/20'

CAR_SERIES_URL = 'https://car.m.autohome.com.cn/ashx/GetSeriesByBrandId.ashx?r=6s&b={}'

HEADERS = {
    'Accept': 'text/html, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN; q=0.5',
    'Connection': 'Keep-Alive',
    'Host': 'zhannei.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
}


def get_brand_ids():
    brand_id = DbUtil.execute("SELECT third_id FROM t_car_brand WHERE status = 1")
    return brand_id


def get_series(brand_ids):
    for brand_id in brand_ids:
        print(CAR_SERIES_URL.format(brand_id[0]))
        b_id = DbUtil.execute("SELECT brand_id FROM t_car_series WHERE `status` = 1 AND brand_id = " + str(brand_id[0]))

        if b_id.__len__() == 0:
            car_series = requests.get(CAR_SERIES_URL.format(brand_id[0]))

            if car_series.status_code == 200:
                car_series.close()
                car_series_json = car_series.json()

                if car_series_json['returncode'] == 0:
                    factory_list = car_series_json['result']['allSellSeries']
                    series_count = 0
                    args = []

                    for factory_item in factory_list:
                        factory_id = factory_item['Id']
                        factory_name = factory_item['name']
                        series_items = factory_item['SeriesItems']

                        for series_item in series_items:
                            sql = "SELECT third_series_id FROM t_car_series WHERE `status` = 1 AND third_series_id = " + str(
                                series_item['id'])
                            third_series_id = DbUtil.execute(sql)

                            if 0 == third_series_id.__len__():
                                series_count = series_count + 1
                                logo_url = series_item['seriesPicUrl']

                                # 图片上传Oss
                                oss_path = "car/series/" + str(brand_id[0])
                                upload = UploadOss(oss_path, 'http:' + logo_url)
                                oss_img_url = upload.upload_oss()

                                sub_args = (DbUtil.get_id(), brand_id[0], factory_id, factory_name, series_item['id'],
                                            series_item['name'], oss_img_url)
                                args.append(sub_args)

                    if 0 < args.__len__():
                        tuple = add_series(args)
                        print(
                            f"插入{factory_name}车系:\n共{series_count}条\n成功插入{tuple[0]}条记录\n插入失败{series_count - tuple[0]}条")

                else:
                    raise Exception("请求失败")


def add_series(args):
    sql = "INSERT INTO t_car_series(`series_id`, `brand_id`, `factory_id`, `factory_name`, `third_series_id`, `series_name`, `series_pic_url`, `create_time`) VALUES(%s, %s, %s, %s, %s, %s, %s, now())"
    tuple = DbUtil.execute_insert(sql, args)
    return tuple


if '__main__' == __name__:
    print("开始抓取车系数据...\n")
    ids = get_brand_ids()
    get_series(ids)
