'''Модуль где храняться все фукнции, которые
не относятся непосредственно к скрапингу сайта,
но помогают форматировать данные или активируют
дополнительные фичи для действия паука.'''
import json
import logging

from scrapy.utils.log import configure_logging

from .settings import START_LINKS


def cut_spaces(value: str) -> str:
    '''Сделал эту функцию, потому что строки
    бывают None + если они не None, то в них
    почти всегда есть пробел.'''
    if value:
        return value.strip()
    return None


def get_links_from_input_json() -> dict:
    '''Достаем ссылки из стартового json.'''
    with open(START_LINKS, encoding='utf-8') as file:
        links = json.load(file)
    return links


def init_logging():
    '''Делаем логи.'''
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='link_spider.log',
        format='%(levelname)s: %(message)s',
        level=logging.ERROR
    )
