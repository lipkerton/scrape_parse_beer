import scrapy
import json
import time
import logging
from scrapy.utils.log import configure_logging 
from scrapy_playwright.page import PageMethod

from ..constants import START_LINKS
from ..items import LinkParserItem, PriceItem, StockItem, AssetsItem, MetadataItem


class LinkSpider(scrapy.Spider):
    # имя паука.
    name = 'link_spider'

    # логи.
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.log',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    # достаем ссылки из json.
    with open(START_LINKS) as file:
        links = json.load(file)

    def start_requests(self):
        '''Запускаем цикл по стартовым ссылкам.'''
        for name, url in self.links.items():
            yield scrapy.Request(
                url=url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod('wait_for_selector', 'div.card-product')
                    ],
                    errback=self.errback
                ),
                callback=self.parse_main_links)

    async def parse_main_links(self, response):
        '''Получаем ссылку из списка ссылок и парсим ее,
        чтобы найти ссылки на страницы пива.'''
        beer_links = self.get_links(response)
        page = response.meta["playwright_page"]
        await page.close()

        for link in beer_links:
            yield scrapy.Request(
                url=link,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_headless = False,
                    playwright_page_methods=[
                        PageMethod('wait_for_selector', 'section.product'),
                        PageMethod(
                            'evaluate',
                            '''() => {document.querySelector('div.switch__wrap > button').click();}'''
                        )
                    ],
                    errback=self.errback
                    
                ),
                callback=self.parse_beer_link
            )
    
    def get_links(self, response) -> list:
        '''Получаем все ссылки из категории.'''
        beer_links = response.xpath(
            '//div[@class="catalog__content"]'
            '/div[3][@class="catalog__list"]'
            '/div[@class="card-product"]'
            '/a[1]/@href'
        ).getall()
        return beer_links
    
    def __get_title(self, response):
        '''Достаем название пива,
        если есть объем достаем и его,
        если есть крепость достаем и ее.'''
        volume = response.xpath(
            '//div[span[contains(., "Крепость")]]'
            "/div/p/text()"
        ).get()
        strength = response.xpath(
            '//div[span[contains(., "Объем")]]'
            '/div/p/text()'
        ).get()
        color = response.xpath(
            '//div[span[contains(., "Цвет")]]'
            '/div/p/text()'
        ).get()
        title = response.css(
            'div.product-card h1::text'
        ).get()
        additional_value = ''
        if volume:
            additional_value += f', {volume}'
        if strength:
            additional_value += f', {strength}'
        if color:
            additional_value += f', {color}'
        if additional_value:
            result = f'{title}'
            result += additional_value
            return result
        return title

    def __get_rpc(self, response):
        '''Достаем уникальный номер.'''
        result = response.xpath(
            '//div[@class="product-card__header"]'
            '/p/text()'
        ).get()
        if result:
            return result.split()[1]
        
    
    def __get_marketing_tags(self, response):
        return response.xpath(
            '//div[@class="product-card-wrap"]'
            '/div[@class="product-card"]'
            '/div[@class="product-card__tags"]'
            '//p/text()'
        ).getall()
    
    def __get_brand(self, response):
        brand = response.xpath(
            '//div[span[contains(., "Производитель")]]'
            '/div/p/text()'
        ).get()
        if brand:
            brand = brand.strip()
        return brand

    def __get_section(self, response):
        return response.xpath(
            '//div[@class="breadcrumbs"]'
            '//p[@class="text text--body-sm text--black"]/text()'
        ).getall()[1:-1]
    
    def __get_price(self, response) -> dict:
        current = response.xpath(
            '//div[@class="button-count button-count--dark product-card__price-button"]'
            '/p/span/text()'
        ).get()
        original = response.xpath(
            '//div[@class="button-count button-count--dark product-card__price-button"]'
            '/p/text()'
        ).get()
        sale_tag = response.xpath(
            '//div[@class="cart-card__price cart-card__sale-price"]'
            '/div/span/text()'
        ).get()

        if sale_tag:
            sale_tag = sale_tag.lstrip('-')


        current = float(current.replace(',', ''))
        original = float(original.split('\xa0')[0])

        price_item = PriceItem()
        
        price_item['current'] = current
        # здесь почти во всех случаях есть символ из юникода,
        # который означает пробел - поэтому я меняю этот символ на пробел.
        price_item['original'] = original
        price_item['sale_tag'] = f'Скидка {sale_tag}'

        return price_item
    
    def __get_stock(self, response):
        beer_number = response.xpath(
            '//div[@class="product__list"]'
            '//p[@class="text text--body-sm card-map__quantity text--black"]/text()'
        ).getall()
        stock_item = StockItem()
        stock_item['in_stock'] = beer_number and True
        stock_item['count'] = sum(map(lambda x: int(x.split('\xa0')[0]), beer_number))
        return stock_item
    
    def __get_assets(self, response):
        main_image = response.xpath('//div[@class="product-info__hero-img-wrap"]/img[1]/@src').get()
        any_other_images = response.xpath('//div[@class="product-info__item product-info__hero"]//img/@src').getall()
        assets_item = AssetsItem()
        assets_item['main_image'] = main_image
        assets_item['set_images'] = any_other_images
        # я не думаю, что там есть 360 фотки и видео пива.
        assets_item['view360'] = []
        assets_item['video'] = []

        return assets_item
    
    def __get_metadata(self, response):
        volume = response.xpath(
            '//div[span[contains(., "Крепость")]]'
            "/div/p/text()"
        ).get()
        strength = response.xpath(
            '//div[span[contains(., "Объем")]]'
            '/div/p/text()'
        ).get()
        color = response.xpath(
            '//div[span[contains(., "Цвет")]]'
            '/div/p/text()'
        ).get()
        temperature = response.xpath(
            '//div[span[contains(., "Температура подачи")]]'
            '/div/p/text()'
        ).get()
        country = response.xpath(
            '//div[span[contains(., "Страна")]]'
            '/div/p/text()'
        ).get()
        english_name = response.xpath(
            '//div[@class="product-card__header"]/div[1]/p/text()'
        ).get()
        producer = response.xpath(
            '//div[span[contains(., "Производитель")]]'
            '/div/p/text()'
        )
        type = response.xpath(
            '//div[span[contains(., "Вид")]]'
            '/div/p/text()'
        )
        description = response.xpath(
            '//p[@class="product-info__description-text"]/text()'
        ).get()
        RPC = self.__get_rpc(response)
        
        # metadata_item = MetadataItem()
        # metadata_item['__description'] = description
        # metadata_item['type'] = type
        # metadata_item['producer'] = producer
        # metadata_item['english_name'] = english_name
        # metadata_item['volume'] = volume
        # metadata_item['color'] = color
        # metadata_item['RPC'] = RPC
        # metadata_item['temperature'] = temperature
        # metadata_item['strength'] = strength
        # metadata_item['country'] = country

        # result = {
        #     __description = description
        #     type = type
        #     metadata_item['producer'] = producer
        #     metadata_item['english_name'] = english_name
        #     metadata_item['volume'] = volume
        #     metadata_item['color'] = color
        #     metadata_item['RPC'] = RPC
        #     metadata_item['temperature'] = temperature
        #     metadata_item['strength'] = strength
        #     metadata_item['country'] = country
        # }

        # return metadata_item



    async def parse_beer_link(self, response):
        '''Получаем страницу пива
         и начинаем вытаскивать из нее данные.'''
        page = response.meta["playwright_page"]
        
        beer_item = LinkParserItem()

        beer_item['timestamp'] = time.time()
        beer_item['title'] = self.__get_title(response)
        beer_item['RPC'] = self.__get_rpc(response)
        beer_item['url'] = response.url
        beer_item['marketing_tags'] = self.__get_marketing_tags(response)
        beer_item['brand'] = self.__get_brand(response)
        beer_item['section'] = self.__get_section(response)
        beer_item['price_data'] = self.__get_price(response)
        beer_item['stock'] = self.__get_stock(response)
        beer_item['assets'] = self.__get_assets(response)
        beer_item['metadata'] = self.__get_metadata(response)
        await page.close()

        yield beer_item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
    




        







