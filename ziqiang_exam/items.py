# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from __future__ import unicode_literals
import scrapy
import re

from datetime import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Compose, Identity


class ZiqiangExamItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TakeFirstLoader(ItemLoader):
    # 自定义item loader
    default_output_processor = TakeFirst()


def extract_date(value):
    regex = re.match('\d{4}/\d{1,2}/\d{1,2}', value.strip())
    create_date = datetime.strptime(regex.group(), '%Y/%m/%d') if regex else value
    return create_date


def extract_unique_integer(value):
    regex = re.match('.*?(\d+).*', value.strip())
    return int(regex.group(1)) if regex else 0


def extract_tags(value):
    tag_list = [element.strip() for element in value if not element.strip().endswith('评论')]
    return ','.join(tag_list)


def remove_comment_in_tags(value):
    # 去掉tags中提取的评论
    if u'评论' in value:
        return ""
    else:
        return value


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(extract_date)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(lambda x: x)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(extract_unique_integer)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(extract_unique_integer)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(extract_unique_integer)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_in_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()


def strip_details(value):
    return [element.strip() for element in value]


class CsdnAuthorItem(scrapy.Item):
    type = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    avatar_url = scrapy.Field(
        output_processor=MapCompose(lambda x: x)
    )
    avatar_path = scrapy.Field()  # imagePipeline里填入
    username = scrapy.Field()
    nick_name = scrapy.Field()
    detail = scrapy.Field(
        input_processor=Compose(strip_details),
        output_processor=Join(',')
    )
    sign = scrapy.Field()
    blog_score = scrapy.Field()
    download_score = scrapy.Field()
    bbs_score = scrapy.Field()
    code_score = scrapy.Field()
    focus_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    fans_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    crawl_date = scrapy.Field()


def csdn_title_trim(value):
    value = re.sub('[\r\t\n]', '', value)
    regex = re.match(r'(.*)\s-\sCSDN博客', value)
    return regex.group(1) if regex else value


def parse_cn_date(value):
    if not (isinstance(value, str) or isinstance(value, unicode)):
        return value
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M')
    except ValueError:
        pass

    regex = re.match(r'(\d{4})[\u5e74](\d{1,2})[\u6708](\d{1,2})[\u65e5]\s(\d{1,2}):(\d{1,2}):(\d{1,2})',
                     value)
    if regex:
        year = int(regex.group(1))
        month = int(regex.group(2))
        day = int(regex.group(3))
        hour = int(regex.group(4))
        minute = int(regex.group(5))
        second = int(regex.group(6))
        return datetime(year, month, day, hour, minute, second)
    else:
        return value


class CsdnArticleItem(scrapy.Item):
    type = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field(input_processor=MapCompose(csdn_title_trim))
    create_date = scrapy.Field(input_processor=MapCompose(parse_cn_date))
    view_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    comment_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    like_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    dislike_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    dig_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    bury_num = scrapy.Field(input_processor=MapCompose(extract_unique_integer))
    crawl_date = scrapy.Field()
