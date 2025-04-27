'''Модуль, где хранятся все настройки scrapy.'''
import pathlib

import dotenv


BOT_NAME = "link_parser"

SPIDER_MODULES = ["link_parser.spiders"]
NEWSPIDER_MODULE = "link_parser.spiders"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 3

CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
    'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

CONCURRENT_REQUESTS = 5 # вместо 16
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 5

BASE_DIR = pathlib.Path(__file__).parent.parent.parent
START_LINKS = pathlib.Path(BASE_DIR) / 'links.json'
DOTENV_FILE = pathlib.Path(BASE_DIR) / '.env'

if DOTENV_FILE.exists():
    dotenv.load_dotenv(DOTENV_FILE)

STEP = 20  # шаг, с которым мы делаем скролл страницы.

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    ' AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X)'
    ' AppleWebKit/605.1.15 (KHTML, like Gecko)'
    ' Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    ' AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    ' AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
]

PROXY_POOL_ENABLED = True

KRASNODAR_COOKIE = (
    "%7B%22uuid%22%3A%224a70f9e0-46ae-11e7-83ff-00155d026416"
    "%22%2C%22name%22%3A%22%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%"
    "BE%D0%B4%D0%B0%D1%80%22%2C%22slug%22%3A%22krasnodar%22%2C"
    "%22longitude%22%3A%2238.975996%22%2C%22latitude%22%3A%2245"
    ".040216%22%2C%22accented%22%3Atrue%7D"
)
