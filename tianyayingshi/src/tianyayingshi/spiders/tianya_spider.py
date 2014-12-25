# -*- coding: gbk-*-
# -*- coding: utf-8-*-
from scrapy.spider import BaseSpider
from scrapy.http import Request
from tianyayingshi.items import TianyayingshiItem
from tianyayingshi.pipelines import MongoDBPipeline

Max_Title_Page = 2
Author_Reply_Str = '-----------------------------'

class TianyaSpider(BaseSpider):
    name = "tianyaSpider"
    allowed_domains = ["bbs.tianya.cn"]
    start_urls = ["http://bbs.tianya.cn/list-filmtv-1.shtml"]
    domain = "http://bbs.tianya.cn"
    pagecount = 0
    title_page_request = True
    title_page_data_index = 0
    title_page_data_list = [] # struct:[content_title, content_link, author_name, click_count, title]
    author_allpage_content_list = []
    reply_allpage_content_list = []
    result_items = []
    def parse(self, response):
    
        if self.title_page_request:
            callback, arg = self.parseTitlePage(response)
        else:
            callback, arg, needRecord = self.parseContentPage(response)
            if needRecord:
                self.SaveData()
                self.ToNextContentPro()
            
        if not callback:
            return
        yield callback(*arg)
        
    def parseTitlePage(self, response): 
        self.pagecount += 1
        trs = response.xpath('//table//tr')
        trs = trs[1:]
        for tr in trs:
            tds = tr.xpath('.//td')
            content_title = tds[0].xpath('a/text()').extract()[0].strip()
            content_link = tds[0].xpath('a/@href').extract()[0]
            author_name = tds[1].xpath('a/text()').extract()[0].strip()
            click_count = tds[2].xpath('text()').extract()[0].strip()
            reply_count = tds[3].xpath('text()').extract()[0].strip()
            #content_title = self.GbkContent(tds[0].xpath('a/text()').extract()[0].strip())
            #content_link = tds[0].xpath('a/@href').extract()[0]
            #author_name = self.GbkContent(tds[1].xpath('a/text()').extract()[0].strip())
            #click_count = tds[2].xpath('text()').extract()[0].strip()
            #reply_count = tds[3].xpath('text()').extract()[0].strip()
            self.title_page_data_list.append([content_title, content_link, author_name, click_count, reply_count])
            
            
            
            
            if len(self.title_page_data_list) >= 5:
                break
                
                
                
                
            
        link = response.xpath('//div[@class="links"]//a[@rel="nofollow"]/@href').extract()[0]
        if not link:
            return None, None
        nextPage = self.domain + link
        
        if self.pagecount == Max_Title_Page:
            self.title_page_request = False
            nextPage = self.domain + self.title_page_data_list[0][1]
        return Request, (nextPage, self.parse)
        
    def parseContentPage(self, response):
        author_content_list = []
        reply_content_list = []
        needRecord = False
        author_name = response.xpath('//meta[@name="author"]/@content').extract()[0]
        contents = response.xpath('//div[@class="atl-item"]')
        first_author_content_list = contents[0].xpath('..//div[@class="bbs-content clearfix"]/text()').extract()
        first_author_content = self.GetContentFromList(first_author_content_list)
        author_content_list.append(first_author_content)
        
        contents = contents[1:]
        
        for content in contents:
            reply_dict = {}
            cur_content_author = content.xpath('.//a/@author').extract()[0]
            cur_content_list = content.xpath('.//div[@class="bbs-content"]/text()').extract()
            cur_content = self.GetContentFromList(cur_content_list)
            if len(cur_content) < 1:
                continue
            #cur_content = self.GbkContent(cur_content)
            if cur_content_author == author_name:
                #if Author_Reply_Str in cur_content:
                if Author_Reply_Str in self.GbkContent(cur_content):
                    continue
                author_content_list.append(cur_content)
            else:
                #cur_content_author = self.GbkContent(cur_content_author)
                reply_dict['reply_author'] = cur_content_author
                reply_dict['reply_content'] = cur_content
                reply_content_list.append(reply_dict)
        self.author_allpage_content_list += author_content_list
        self.reply_allpage_content_list += reply_content_list
        nextPage = self.GetNextPageLink(response)
        if not nextPage:
            needRecord = True
            nextPage = self.GetNextContentLink()
            if not nextPage:
                return None, None, needRecord
        return Request, (nextPage, self.parse), needRecord
        
    def GetNextContentLink(self):
        next_index = self.title_page_data_index + 1
        if next_index == len(self.title_page_data_list):
            return ''
        nextPage = self.domain + self.title_page_data_list[next_index][1]
        return nextPage
    
    def GetNextPageLink(self, response):
        link = ''
        page_a_list = response.xpath('//div[@class="atl-pages"]//a')
        if len(page_a_list) < 1:
            pass
        else:
            a_site = page_a_list[-1]
            a_text = a_site.xpath('text()').extract()[0]
            a_text = self.GbkContent(a_text)
            try:
                a_text = int(a_text)
            except:
                link = a_site.xpath('@href').extract()[0]
        if not link:
            return ''
        nextPage = self.domain + link
        return nextPage
        
    def GetContentFromList(self, list):
        content = ''
        for item in list:
            item = item.strip()
            content += item
        return content
    
    def GbkContent(self, content):
        try:
            content = content.encode('gbk')
        except:
            pass
        return content
        
    def ToNextContentPro(self):
        self.author_allpage_content_list = []
        self.reply_allpage_content_list = []
        self.title_page_data_index += 1
        return
        
    def SaveData(self):
        item = TianyayingshiItem()
        item['title'] = self.title_page_data_list[self.title_page_data_index][0]
        item['author_name'] = self.title_page_data_list[self.title_page_data_index][2]
        item['click_count'] = self.title_page_data_list[self.title_page_data_index][3]
        item['reply_count'] = self.title_page_data_list[self.title_page_data_index][4]
        item['author_content_list'] = self.author_allpage_content_list
        item['reply_content_list'] = self.reply_allpage_content_list
        pipiline = MongoDBPipeline()
        pipiline.process_item(item, self)
    
        return

