BOT_NAME = 'scientific_scraper'
SPIDER_MODULES = ['scientific_scraper.spiders']
NEWSPIDER_MODULE = 'scientific_scraper.spiders'

USER_AGENT = 'scientific_scraper (+http://www.yourdomain.com)'
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
COOKIES_ENABLED = False

ITEM_PIPELINES = {
    'scientific_scraper.pipelines.DataCleaningPipeline': 100,
    'scientific_scraper.pipelines.DuplicateFilterPipeline': 200,
    'scientific_scraper.pipelines.MongoDBPipeline': 300,
}

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'scientific_articles'

LOG_LEVEL = 'INFO'

FEEDS = {
    'output/%(name)s_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
}
