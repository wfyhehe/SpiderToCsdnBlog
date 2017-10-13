# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re

import requests
import scrapy
from datetime import datetime

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ziqiang_exam.items import TakeFirstLoader, CsdnAuthorItem, CsdnArticleItem
from ziqiang_exam.utils.common import get_md5
from ziqiang_exam.utils.const import CSDN_AUTHOR, CSDN_ARTICLE_OLD, CSDN_ARTICLE_NEW


class CsdnblogSpider(CrawlSpider):
    name = 'csdnblog'
    allowed_domains = ['blog.csdn.net', 'my.csdn.net']
    start_urls = ['http://my.csdn.net/']

    rules = (
        Rule(LinkExtractor(allow=r'article/details/', allow_domains=r'blog.csdn.net'),
             callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'my.csdn.net/.+', allow_domains='my.csdn.net'),
             callback='parse_author', follow=True),
        Rule(LinkExtractor(allow=r'', allow_domains='my.csdn.net/?$'), follow=True),
        Rule(LinkExtractor(allow_domains=r'blog.csdn.net'), follow=True),
    )

    def parse_author(self, response):
        item_loader = TakeFirstLoader(item=CsdnAuthorItem(), response=response)

        username_re = re.match(r'.*/(\w+)/?$', response.url)
        username = username_re.group(1) if username_re else ''
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/61.0.3163.100 Safari/537.36'}
        ajax_response = requests.get('http://my.csdn.net/service/main/getSorce?username=%s' % username,
                                     headers=headers)
        data = json.loads(ajax_response.content)
        score_dict = data['result']['score']
        blog_score = score_dict['blog']['total_score']
        bbs_score = score_dict['bbs']['total_score']
        download_score = score_dict['download']['total_score']
        code_score = score_dict['code']['total_score']

        item_loader.add_value('type', CSDN_AUTHOR)
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('avatar_url', '.persional_property .person-photo img::attr(src)')
        item_loader.add_value('username', username)
        item_loader.add_css('nick_name', '.person-nick-name span::text')
        item_loader.add_css('detail', '.person-detail::text')
        item_loader.add_css('sign', '.person-sign::text')
        item_loader.add_value('blog_score', blog_score)
        item_loader.add_value('download_score', bbs_score)
        item_loader.add_value('bbs_score', download_score)
        item_loader.add_value('code_score', code_score)
        item_loader.add_css('focus_num', '.focus_num b::text')
        item_loader.add_css('fans_num', '.fans_num b::text')
        item_loader.add_value('crawl_date', datetime.now())

        author_item = item_loader.load_item()

        yield author_item  # 传给pipeline

    def parse_article(self, response):
        # 通过是否存在 id='container'的元素来确定是旧版还是新版，有#container的是旧版
        container = response.css('#container')

        item_loader = TakeFirstLoader(item=CsdnArticleItem(), response=response)
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('crawl_date', datetime.now())

        if len(container) > 0:  # 旧版
            item_loader.add_value('type', CSDN_ARTICLE_OLD)
            item_loader.add_css('author', '.user_name::text')
            item_loader.add_css('title', 'title::text')
            item_loader.add_css('create_date', '.link_postdate::text')
            item_loader.add_css('view_num', '.link_view::text')
            comment_num = response.css('.link_comments::text').extract()[1]
            item_loader.add_value('comment_num', comment_num)
            item_loader.add_css('dig_num', '#btnDigg dd::text')
            item_loader.add_css('bury_num', '#btnBury dd::text')

        else:  # 新版
            item_loader.add_value('type', CSDN_ARTICLE_NEW)
            item_loader.add_css('author', '#uid::text')
            item_loader.add_css('title', 'title::text')
            item_loader.add_css('create_date', '.artical_tag .time::text')
            item_loader.add_css('view_num', '.article_bar .icon-read+span::text')
            item_loader.add_css('comment_num', '.article_bar .icon-pinglun+span::text')
            item_loader.add_css('like_num', '.article_bar .btn-like .txt::text')

        article_item = item_loader.load_item()
        yield article_item
