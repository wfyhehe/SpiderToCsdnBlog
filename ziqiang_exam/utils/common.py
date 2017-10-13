#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

__author__ = 'wfy'
__date__ = '2017/10/10 22:51'


def get_md5(url):
    if isinstance(url, unicode):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print get_md5('http://jobbole.com')
