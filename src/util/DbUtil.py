# -*- coding:utf-8 -*-
# coding:utf-8
# https://blog.csdn.net/tomorrow13210073213/article/details/72809762

import configparser
import requests
import pymysql
import json

__author__ = 'zxk175'
__date__ = '2018/12/20'

cf = configparser.ConfigParser()
cf.read("./conf/conf.ini")

env = "local"

DB = cf.get(env, "DB")
USER = cf.get(env, "USER")
PASSWORD = cf.get(env, "PASSWORD")
HOST = cf.get(env, "HOST")
PORT = cf.get(env, "PORT")
CHARSET = cf.get(env, "CHARSET")


def get_id():
    url = "http://test.szsdyc.cn/snow_id/v1"
    data = requests.get(url)
    return json.loads(data.text).get("data")


def get_connect():
    try:
        conn = pymysql.connect(HOST, USER, PASSWORD, DB, charset=CHARSET)
        conn.ping(reconnect=True)
        return conn
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e


def execute(sql_str):
    if sql_str is None:
        raise Exception("参数不能为空：sql_str")
    if len(sql_str) == 0:
        raise Exception("参数不能为空：sql_str")
    try:
        conn = get_connect()
        cur = conn.cursor()
        cur.execute(sql_str)
        data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e


# 插入数据，返回数据主键
def execute_insert(insert_str, data):
    if insert_str is None:
        raise Exception("参数不能为空：sql_str")
    if len(insert_str) == 0:
        raise Exception("参数不能为空：sql_str")
    try:
        conn = get_connect()
        cur = conn.cursor()
        row_count = cur.executemany(insert_str, data)
        last_id = conn.insert_id()
        conn.commit()
        cur.close()
        conn.close()
        return row_count, last_id
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e


# 执行带参数的删除
def execute_delete(select_str, data):
    if select_str is None:
        raise Exception("参数不能为空：sql_str")
    if len(select_str) == 0:
        raise Exception("参数不能为空：sql_str")
    try:
        conn = get_connect()
        cur = conn.cursor()
        cur.execute(select_str, data)
        data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e


# 更新数据，返回更新条数
def execute_update(update_str, data):
    if update_str is None:
        raise Exception("参数不能为空：update_str")
    if len(update_str) == 0:
        raise Exception("参数不能为空：update_str")
    try:
        conn = get_connect()
        cur = conn.cursor()
        count = cur.execute(update_str, data)
        conn.commit()
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e


# 执行带参数的查询，返回查询结果
def execute_select(select_str, data):
    if select_str is None:
        raise Exception("参数不能为空：sql_str")
    if len(select_str) == 0:
        raise Exception("参数不能为空：sql_str")
    try:
        conn = get_connect()
        cur = conn.cursor()
        cur.execute(select_str, data)
        data = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        raise e
