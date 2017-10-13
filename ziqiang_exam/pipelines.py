# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import re

import MySQLdb
import MySQLdb.cursors
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline

from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from twisted.python.failure import Failure

from ziqiang_exam.items import CsdnArticleItem, CsdnAuthorItem


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '190035', 'scrapy',
                                    charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
               insert into article(title, create_date, url, url_object_id, front_image_url,
               front_image_path, comment_nums, fav_nums, praise_nums, tags, content)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           """
        if len(item['front_image_url']) > 0:
            front_image_url = item['front_image_url'][0]
        else:
            front_image_url = None
        self.cursor.execute(insert_sql,
                            (item['title'], item['create_date'], item['url'],
                             item['url_object_id'], front_image_url, item['front_image_path'],
                             item['comment_nums'], item['fav_nums'], item['praise_nums'],
                             item['tags'], item['content']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    # 异步写入mysql
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入异常
        print failure

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                       insert into article(title, create_date, url, url_object_id, front_image_url,
                       front_image_path, comment_nums, fav_nums, praise_nums, tags, content)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   """
        if len(item['front_image_url']) > 0:
            front_image_url = item['front_image_url'][0]
        else:
            front_image_url = None
        cursor.execute(insert_sql,
                       (item['title'], item['create_date'], item['url'],
                        item['url_object_id'], front_image_url, item['front_image_path'],
                        item['comment_nums'], item['fav_nums'], item['praise_nums'],
                        item['tags'], item['content']))
        return item


class ArticleImagePipeline(ImagesPipeline):  # 将图片下载到本地，在item里加入图片的本地路径
    def item_completed(self, results, item, info):

        if 'front_image_url' in item:
            image_file_path = None
            for ok, value in results:
                image_file_path = value.get('path', '')
            item['front_image_path'] = image_file_path
        return item


class CsdnAuthorImagePipeline(ImagesPipeline):  # 将图片下载到本地，在item里加入图片的本地路径
    def get_media_requests(self, item, info):  # 在所有图片请求的headers加上referer, 否则会被403
        ret = []
        regex = re.compile(r'.*/._(\w+)\.jpg$')
        refered_prefix = 'http://my.csdn.net/'
        for url in item.get(self.images_urls_field, []):
            username = regex.match(url).group(1) if regex.match(url) else ''
            headers = {
                'referer': refered_prefix + username
            }
            ret.append(Request(url, headers=headers))
        return ret

    def item_completed(self, results, item, info):
        if 'avatar_url' in item:
            avatar_file_path = None
            for ok, value in results:
                if isinstance(value, Failure):
                    return item
                avatar_file_path = value['path']
            item['avatar_path'] = avatar_file_path
        return item


class CsdnArticleTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        if not isinstance(item, CsdnArticleItem):
            return item
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print failure

    def do_insert(self, cursor, item):
        insert_sql = """
                                   insert into csdn_article(title, url, url_object_id, author, view_num,
                                   comment_num, like_num, dig_num, bury_num, create_date, crawl_date)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               """
        cursor.execute(insert_sql,
                       (item.get('title'), item.get('url'), item.get('url_object_id'), item.get('author'),
                        item.get('view_num'), item.get('comment_num'), item.get('like_num'), item.get('dig_num'),
                        item.get('bury_num'), item.get('create_date'), item.get('crawl_date')))
        return item


class CsdnAuthorTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        if not isinstance(item, CsdnAuthorItem):
            return item
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print failure

    def do_insert(self, cursor, item):
        insert_sql = """
                       insert into csdn_author(url, url_object_id, avatar_url,
                       avatar_path, username, nick_name, detail, sign, blog_score,
                       download_score, bbs_score, code_score, focus_num,
                       fans_num, crawl_date)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   """
        if len(item.get('avatar_url')) > 0:
            avatar_url = item['avatar_url'][0]
        else:
            avatar_url = None
        cursor.execute(insert_sql,
                       (item.get('url'), item.get('url_object_id'), avatar_url, item.get('avatar_path'),
                        item.get('username'), item.get('nick_name'), item.get('detail'),
                        item.get('sign'), item.get('blog_score'), item.get('download_score'),
                        item.get('bbs_score'), item.get('code_score'), item.get('focus_num'),
                        item.get('fans_num'), item.get('crawl_date')))
        return item
