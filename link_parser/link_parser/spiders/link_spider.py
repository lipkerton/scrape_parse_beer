'''Модуль, где содержится код пауков.'''
import random
import time
import typing

import scrapy
import scrapy.http
import scrapy.http.response
import scrapy.http.response.html
from scrapy_playwright.page import PageMethod

from ..items import LinkParserItem
from ..methods import cut_spaces, get_links_from_input_json, init_logging
from ..settings import KRASNODAR_COOKIE, STEP, USER_AGENTS


class LinkSpider(scrapy.Spider):
    '''Получаем json с стартовыми ссылками,
    проходимся по ним, открываем личные страницы
    каждого пива, вытаскиваем информацию с личных страниц.'''

    name = 'link_spider'  # имя паука.
    init_logging()  # логи.
    # достаем ссылки из json.
    links = get_links_from_input_json()

    def start_requests(
            self
    ) -> typing.Generator[scrapy.http.response.html.HtmlResponse]:
        '''Запускаем цикл по стартовым ссылкам.'''
        for _, url in self.links.items():
            yield scrapy.Request(
                url=url,
                cookies={
                    "alkoteka_locality": KRASNODAR_COOKIE
                },
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        # PageMethod('wait_for_selector', 'div.card-product')
                        PageMethod('wait_for_selector', 'div.catalog__list')
                        ],
                    errback=self.errback
                    ),
                callback=self.parse_main_links,
                headers={
                    "User-Agent": USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]
                }
            )


    async def parse_main_links(
            self, response: scrapy.http.response.html.HtmlResponse
    ) -> typing.AsyncGenerator[scrapy.http.response.html.HtmlResponse]:
        '''Получаем ссылку из списка ссылок и парсим ее,
        чтобы найти ссылки на страницы пива.'''

        beer_total_number = int(response.xpath(
            '//p[@class="catalog-amount text text--body-sm"]/text()'
        ).get().split()[1])
        page = response.meta["playwright_page"]
        beer_links = self.get_links(response)

        for _ in range(0, beer_total_number, STEP):
            # если просто крутить мышкой, то нужно крутить по 10 пикселей
            # в цикле - это очень долго, а если крутить сразу по 100+ пикселей,
            # то есть огромный шанс вылететь в footer и тогда ничего уже крутиться
            # не будет, поэтому нужно вычесть футер из размера страницы и скроллить
            # по результату.
            await page.evaluate(
                '''() => {
                    const footer = document.querySelector('footer');
                    const footerHeight = footer.offsetHeight;
                    window.scrollTo({
                        top: document.body.scrollHeight - footerHeight - 100,
                        behavior: 'smooth'
                    });
                };'''
            )
            await page.wait_for_timeout(1000)
            current_scroll = await page.evaluate("window.pageYOffset")
            print(f"Текущая позиция скролла: {current_scroll}")

        html = await page.content()
        scrolled_page = scrapy.Selector(text=html)
        beer_links = self.get_links(scrolled_page)
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
                        # эта строчка нужна, чтобы нажать на свич на странице,
                        # я пытался разными методами, но получается только так.
                        PageMethod(
                            'evaluate',
                            '''() =>
                            {document.querySelector('div.switch__wrap > button').click();
                            }'''
                        )
                    ],
                    errback=self.errback
                ),
                callback=self.parse_beer_link,
                headers={
                    "User-Agent": USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]
                }
            )

    def get_links(self, response:scrapy.http.response.html.HtmlResponse) -> list[str]:
        '''Получаем все ссылки из категории.'''
        beer_links = response.xpath(
            '//div[@class="catalog__content"]'
            '/div[3][@class="catalog__list"]'
            '//div[@class="card-product"]'
            '/a[1]/@href'
        ).getall()
        return beer_links

    def __get_title(self, response:scrapy.http.response.html.HtmlResponse) -> str:
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

    def __get_rpc(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> str:
        '''Достаем уникальный номер.'''
        result = response.xpath(
            '//div[@class="product-card__header"]'
            '/p/text()'
        ).get()
        if result:
            return result.split()[1]

    def __get_marketing_tags(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> str:
        return response.xpath(
            '//div[@class="product-card-wrap"]'
            '/div[@class="product-card"]'
            '/div[@class="product-card__tags"]'
            '//p/text()'
        ).getall()

    def __get_brand(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> str:
        '''Получаем бренд пива.'''
        brand = cut_spaces(response.xpath(
            '//div[span[contains(., "Производитель")]]'
            '/div/p/text()'
        ).get())
        return brand

    def __get_section(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> str:
        '''Получаем секцию, где находится пиво.
        Я использую срез [1:-1], потому что
        0 - это "Главная", а последний элемент - имя самого пива.'''
        return response.xpath(
            '//div[@class="breadcrumbs"]'
            '//p[@class="text text--body-sm text--black"]/text()'
        ).getall()[1:-1]

    def __get_price(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> dict[str, float]:
        '''Получаем цену из надписей на кнопках.
        Там есть старая и новая цены + скидка на карточке.
        Цены превращаем в float + убираем все лишние символы.
        А скидку форматируем и превращаем в красивую строку.'''
        current_price = response.xpath(
            '//div[@class="button-count button-count--dark product-card__price-button"]'
            '/p/span/text()'
        ).get()
        original_price = response.xpath(
            '//div[@class="button-count button-count--dark product-card__price-button"]'
            '/p/text()'
        ).get()
        sale_tag_price = response.xpath(
            '//div[@class="cart-card__price cart-card__sale-price"]'
            '/div/span/text()'
        ).get()

        if sale_tag_price:
            sale_tag_price = sale_tag_price.lstrip('-')

        # нужно заменить запятые и убрать символы юникода
        # для перевода в float.
        current_price = float(current_price.replace(',', ''))
        original_price = float(original_price.replace(',', '').split('\xa0')[0])

        return dict(
            current = current_price,
            original = original_price,
            sale_tag = f'Скидка {sale_tag_price}'
        )

    def __get_stock(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> dict[bool, int]:
        '''Для этой функции нужно было переключить кнопку:
        Нужно было открыть список всех магазинов вместо карты
        и посчитать сумму всех их товаров.'''
        beer_number = response.xpath(
            '//div[@class="product__list"]'
            '//p[@class="text text--body-sm card-map__quantity text--black"]/text()'
        ).getall()

        return dict(
            in_stock = beer_number and True,
            # эта штука проходи по всем карточкам в списке магазинов,
            # форматирует строки и превращает количество в int,
            # а потом все суммируется.
            count = sum(map(lambda x: int(x.split('\xa0')[0]), beer_number))
        )

    def __get_assets(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> dict[str, list[str]]:
        '''Достаем всю медиа со страницы.'''
        main_image_asset = response.xpath(
            '//div[@class="product-info__hero-img-wrap"]/img[1]/@src'
        ).get()
        any_other_images_asset = response.xpath(
            '//div[@class="product-info__item product-info__hero"]//img/@src'
        ).getall()

        return dict(
            main_image = main_image_asset,
            set_images = any_other_images_asset,
            view360 = [],
            video = []
        )

    def __get_metadata(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> dict[str, str]:
        '''Достаем все харакетристики.'''
        volume_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Объем")]]'
            '/div/p/text()'
        ).get())
        strength_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Крепость")]]'
            "/div/p/text()"
        ).get())
        color_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Цвет")]]'
            '/div/p/text()'
        ).get())
        temperature_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Температура подачи")]]'
            '/div/p/text()'
        ).get())
        country_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Страна")]]'
            '/div/p/text()'
        ).get())
        english_name_meta = cut_spaces(response.xpath(
            '//div[@class="product-card__header"]/div[1]/p/text()'
        ).get())
        producer_meta = cut_spaces(response.xpath(
            '//div[span[contains(., "Производитель")]]'
            '/div[1]/p[1]/text()'
        ).get())
        type_meta = cut_spaces(response.xpath(
            '//div[span[text() = "Вид"]]'
            '/div[1]/p[1]/text()'
        ).get())
        description_meta = response.xpath(
            '//p[@class="product-info__description-text"]/text()'
        ).get()

        result = dict(
            __description = description_meta,
            type = type_meta,
            producer = producer_meta,
            english_name = english_name_meta,
            volume = volume_meta,
            color = color_meta,
            RPC = self.__get_rpc(response),
            temperature = temperature_meta,
            strength = strength_meta,
            country = country_meta
        )
        return result



    async def parse_beer_link(
        self, response:scrapy.http.response.html.HtmlResponse
    ) -> typing.AsyncGenerator[LinkParserItem]:
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
        # много путешествовал по сайту, но не выидел карточек
        # c разными пивными вариантами, поэтому пусть будет 1.
        beer_item['variants'] = 1

        await page.wait_for_timeout(random.randint(1000, 3000))
        await page.close()

        yield beer_item

    async def errback(
        self, failure:scrapy.http.response.html.HtmlResponse
    ) -> None:
        '''Закрываем страницу экстренно,  
        чтобы не потерять память.'''
        page = failure.request.meta["playwright_page"]
        await page.close()
