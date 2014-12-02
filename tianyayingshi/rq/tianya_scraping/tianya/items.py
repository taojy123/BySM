import scrapy

class TianYaItem(scrapy.Item):
    title = scrapy.Field()
    no_of_clicks = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    commenters_name = scrapy.Field()
    no_of_replies = scrapy.Field()
    content_of_comments = scrapy.Field()
    last_reply_datetime = scrapy.Field()
    links = scrapy.Field()
    
