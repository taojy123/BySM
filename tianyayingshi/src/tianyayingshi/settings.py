BOT_NAME = 'tianyayingshi'

SPIDER_MODULES = ['tianyayingshi.spiders']
NEWSPIDER_MODULE = 'tianyayingshi.spiders'

ITEM_PIPELINES =['tianyayingshi.pipelines.MongoDBPipeline',]

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "MongoDB"
MONGODB_COLLECTION = "blogposts"
