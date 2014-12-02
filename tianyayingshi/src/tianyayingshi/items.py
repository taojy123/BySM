from scrapy.item import Item, Field 

class TianyayingshiItem(Item):
    title = Field()
    author_name = Field()
    click_count = Field()
    reply_count = Field()
    author_content_list = Field()
    reply_content_list = Field()
