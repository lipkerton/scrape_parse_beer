import scrapy


class PriceData(scrapy.Item):
    current = scrapy.Field()
    original = scrapy.Field()
    sale_tag = scrapy.Field()


class Stock(scrapy.Item):
    in_stock = scrapy.Field()
    count = scrapy.Field()


class Assets(scrapy.Item):
    main_image = scrapy.Field()
    set_images = scrapy.Field(serializer=list)
    view360 = scrapy.Field(serializer=list)
    video = scrapy.Field(serializer=list)


class LinkParserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    RPC = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    # marketing_tags = scrapy.Field(serializer=list)
    # brand = scrapy.Field()
    # section = scrapy.Field(serializer=list)
    # price_data = PriceData()
    # stock = Stock()
    # assets = Assets()


