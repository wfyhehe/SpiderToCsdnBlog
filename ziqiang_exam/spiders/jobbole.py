#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from datetime import datetime
import scrapy
from scrapy.http import Request
import urlparse

from scrapy.loader import ItemLoader

from ziqiang_exam.items import JobboleArticleItem, TakeFirstLoader
from ziqiang_exam.utils.common import get_md5

__author__ = 'wfy'
__date__ = '2017/10/10 12:27'


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1、获取文章列表页中的文章url并交给scrapy下载后解析
        2、获取下一页的url并交给scrapy进行下载，下载完成后交给parse

        """
        # 解析列表页中所有文章url并交给scrapy下载后进行解析
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')

            yield Request(url=urlparse.urljoin(response.url, post_url),
                          meta={'front_image_url': urlparse.urljoin(response.url, image_url)},
                          callback=self.parse_detial)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(url=urlparse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detial(self, response):
        """
        提取文章具体字段
        """

        # article_item = JobboleArticleItem()
        #
        # front_image_url = response.meta.get('front_image_url', '')  # 文章封面图
        # # article_id_re = re.match('.*?(\d+).*', response.url)
        # # article_id = article_id_re.group(1) if article_id_re else ''
        # # title = response.xpath('//*[@id="post-%s"]/div[1]/h1/text()' % article_id
        # #                        ).extract_first()
        # title = response.css('.entry-header h1::text').extract_first()
        # # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()'
        # #                              ).extract_first().strip()[:-1].strip()
        # create_date = response.css('.entry-meta-hide-on-mobile::text').extract_first().strip()
        # create_date_re = re.match('\d{4}/\d{1,2}/\d{1,2}', create_date)
        # create_date = create_date_re.group() if create_date_re else create_date
        #
        # # praise_nums = response.xpath('//*[@id="%svotetotal"]/text()'
        # #                              ).extract_first()
        # praise_nums = response.css('.post-adds .vote-post-up h10::text').extract_first()
        # praise_nums_re = re.match('.*?(\d+).*', praise_nums)
        # praise_nums = praise_nums_re.group(1) if praise_nums_re else '0'
        #
        # # fav_nums = response.xpath('//*[@id="post-%s"]/div[3]/div[9]/span[2]/text()' % article_id
        # #                           ).extract_first()
        # fav_nums = response.css('.post-adds .bookmark-btn::text').extract_first()
        # fav_nums_re = re.match('.*?(\d+).*', fav_nums)
        # fav_nums = fav_nums_re.group(1) if fav_nums_re else '0'
        #
        # # comment_nums = response.xpath('//*[@id="post-%s"]/div[3]/div[9]/a/span/text()' % article_id
        # #                               ).extract_first()
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract_first()
        # comment_nums_re = re.match('.*?(\d+).*', comment_nums)
        # comment_nums = comment_nums_re.group(1) if comment_nums_re else '0'
        #
        # # content = response.xpath('//div[@class="entry"]').extract()
        #
        # content = response.css('.entry').extract()
        # # tag_list = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element.strip() for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        #
        # article_item['title'] = title
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # try:
        #     create_date = datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.now().date()
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['praise_nums'] = praise_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        # 通过item loader加载item
        item_loader = TakeFirstLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_value('front_image_url', response.meta.get('front_image_url'))
        item_loader.add_css('comment_nums', 'a[href="#article-comment"] span::text')
        item_loader.add_css('fav_nums', '.post-adds .bookmark-btn::text')
        item_loader.add_css('praise_nums', '.post-adds .vote-post-up h10::text')
        item_loader.add_css('tags', '.entry-meta-hide-on-mobile a::text')
        item_loader.add_css('content', '.entry')
        article_item = item_loader.load_item()

        yield article_item  # 传给pipeline
