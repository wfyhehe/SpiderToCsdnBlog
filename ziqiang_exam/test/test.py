#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests
import MySQLdb

import re

from datetime import datetime

__author__ = 'wfy'
__date__ = '2017/10/10 17:07'
# headers = {
#     'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
#                   ' Chrome/61.0.3163.100 Safari/537.36'}
# response = requests.get('http://my.csdn.net/service/main/getSorce?username=zhangerqing', headers=headers)
# data = json.loads(response.content)
# blog_score = data['result']['score']['blog']['total_score']
# bbs_score = data['result']['score']['bbs']['total_score']
# download_score = data['result']['score']['download']['total_score']
# code_score = data['result']['score']['bbs']['total_score']
# print [blog_score, download_score, bbs_score, code_score]

# import urlparse
#
# url1 = 'http://www.baidu.com'
# url2 = '165456'
# print urlparse.urljoin(url1, url2)
# string = '\r\n\r\n            2017/10/03 \xb7'
# print re.match('.*\d.*', string.strip()).group()


# conn = MySQLdb.connect('127.0.0.1', 'root', '190035', 'scrapy',
#                        charset="utf8", use_unicode=True)
# cursor = conn.cursor()
#
# sql = """insert into article(title, create_date, url, url_object_id, front_image_url,
#          front_image_path, comment_nums, fav_nums, praise_nums, tags, content)
#          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#       """
# cursor.execute(sql, ('title', '2018/10/11', 'http://www.flyingwang.com/', '123456',
#                      'http://image.flyingwang.com/111111/', 'D:/image/312132', '1', '4', '2',
#                      'Java,Web', '1234657894894561\r\n156123456\r\n546465\t\t46894  465fe4684\r\n'))
# conn.commit()
# print datetime.strptime('2017年10月12日 10:41', '%Y-%m-%d %H:%M')
# cn_time = '2017年10月08日 12:38:42'
# regex = re.match(r'(\d{4})[\u5e74](\d{1,2})[\u6708](\d{1,2})[\u65e5]\s(\d{1,2}):(\d{1,2}):(\d{1,2})}',
#                  cn_time)
# if regex:
#     year = int(regex.group(1))
#     month = int(regex.group(2))
#     day = int(regex.group(3))
#     hour = int(regex.group(4))
#     minute = int(regex.group(5))
#     second = int(regex.group(6))
#     ret = datetime(year, month, day, hour, minute, second)
#     print ret
# txt = '''LeakCanary原理解析 \r- 王三\t\t的专栏 \r\n- CSDN博客'''
# txt = re.sub('[\r\t\n]', '', txt)
# regex = re.findall(r' - CSDN博客', txt)
# print regex
url = u'http://avatar.csdn.net/F/B/D/1_wl0khr68.jpg'
regex = re.compile('.*/._(\w+)\.jpg$')
print regex.match(url).group(1)

username = regex.match(url).group(1) if regex.match(url) else ''
