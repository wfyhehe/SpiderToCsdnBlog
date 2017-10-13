#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from scrapy.cmdline import execute

import sys
import os

from ziqiang_exam.spiders.jobbole import JobboleSpider
from ziqiang_exam.spiders.csdnblog import CsdnblogSpider

__author__ = 'wfy'
__date__ = '2017/10/10 12:34'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(['scrapy', 'crawl', JobboleSpider.name])
execute(['scrapy', 'crawl', CsdnblogSpider.name])

