import scrapy


# class MetadataItem(scrapy.Item):
#     __description = scrapy.Field()
#     RPC = scrapy.Field()
#     type = scrapy.Field()
#     color = scrapy.Field()
#     producer = scrapy.Field()
#     volume = scrapy.Field()
#     english_name = scrapy.Field()
#     country = scrapy.Field()
#     temperature = scrapy.Field()

    

class AssetsItem(scrapy.Item):
    main_image = scrapy.Field()
    set_images = scrapy.Field()
    view360 = scrapy.Field()
    video = scrapy.Field()


class StockItem(scrapy.Item):
    in_stock = scrapy.Field()
    count = scrapy.Field(serializer=list)


class PriceItem(scrapy.Item):
    current = scrapy.Field()
    original = scrapy.Field()
    sale_tag = scrapy.Field()


class LinkParserItem(scrapy.Item):
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


