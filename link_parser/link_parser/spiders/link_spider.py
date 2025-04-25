import scrapy
import json
import time

from ..constants import START_LINKS
from ..items import LinkParserItem


class LinkSpider(scrapy.Spider):

    name = 'link_spider'
    with open(START_LINKS) as file:
        links = json.load(file)

    def start_requests(self):
        '''Запускаем цикл по стартовым ссылкам.'''
        for name, url in self.links.items():
            yield scrapy.Request(url=url, meta={'playwright': True}, callback=self.parse_main_links)

    def parse_main_links(self, response):
        beer_links = self.get_links(response=response)
        yield from response.follow_all(beer_links, meta={'playwright': True}, callback=self.parse_beer_links)
    
    def get_links(self, response):
        return response.xpath('//div[@class="card-product"]/a/@href').getall()
    
    def parse_beer_links(self, response):

        def extract_with_css(query):
            return response.css(query).get(default="").strip()
        
        timestamp = time.time()
        title = extract_with_css('div.product-card h1::text')
        rpc = extract_with_css('div.product-card__header div p::text')
        url = response.url
        


        







