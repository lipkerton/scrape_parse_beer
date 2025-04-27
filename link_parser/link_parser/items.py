'''Модуль, в котором описаны объекты.
Эти объекты помогают данным превратиться в
формат json на выходе.'''
import scrapy


class LinkParserItem(scrapy.Item):
    '''Делаем класс, в который будем
    запаковывать информацию о пиве.'''
    timestamp = scrapy.Field()
    RPC = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    marketing_tags = scrapy.Field(serializer=list)
    brand = scrapy.Field()
    section = scrapy.Field()
    price_data = scrapy.Field()
    stock = scrapy.Field()
    assets = scrapy.Field()
    metadata = scrapy.Field()
    variants = scrapy.Field()
