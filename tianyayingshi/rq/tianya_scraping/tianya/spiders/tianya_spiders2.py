# -*- coding: utf-8-*-
import urlparse
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from pymongo import Connection

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
#from tianya.items import TianYaItem

class tianya_spiders2(scrapy.Spider):
    name = "tianya_spiders2"
    allowed_domains = ["bbs.tianya.cn"]
    start_urls = ["http://bbs.tianya.cn/post-filmtv-521118-1.shtml"]
    domain = "http://bbs.tianya.cn"
    def parse(self, response):

        for sel in response.xpath("//div[contains(@class,'bbs-content')]"):
            for content in sel.xpath("text()").extract():
                content = content.strip()
                print content

            nextPage = ""
        for link in sel.xpath("//a[@class='js-keyboard-next']/@href").extract():
            if "post-filmtv-" in link:
                nextPage = self.domain+link
            yield Request(nextPage,self.parse)

    

