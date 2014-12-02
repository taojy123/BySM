# -*- coding: gbk-*-
# -*- coding: utf-8-*-
import urlparse
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from pymongo import Connection

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from tianya.items import TianYaItem

class tianya_spiders(scrapy.Spider):
    name = "tianya_spiders"
    allowed_domains = ["bbs.tianya.cn"]
    start_urls = ["http://bbs.tianya.cn/list-filmtv-1.shtml"]
    domain = "http://bbs.tianya.cn"
    def parse(self, response):

        for sel in response.xpath("//table[contains(@class, 'tab-bbs-list')]/tbody"):
            for item in sel.xpath("tr/td/a/text()").extract():
                item = item.strip()
                item = item.replace('\n','')
                print item

            nextPage = ""
        for link in sel.xpath("//a[@rel='nofollow']/@href").extract():
            if "nextid" in link:
                nextPage = self.domain+link
                
        yield Request(nextPage,self.parse)

