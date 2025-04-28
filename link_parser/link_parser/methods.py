'''Модуль где храняться все фукнции, которые
не относятся непосредственно к скрапингу сайта,
но помогают форматировать данные или активируют
дополнительные фичи для действия паука.'''
import json
import logging
import typing

from scrapy.utils.log import configure_logging

from .settings import START_LINKS


def cut_spaces(value: typing.Optional[str]) -> typing.Optional[str]:
    '''Сделал эту функцию, потому что строки
    бывают None + если они не None, то в них
    почти всегда есть пробел.'''
    if value:
        return value.strip()
    return None


def get_links_from_input_json() -> dict[str, str]:
    '''Достаем ссылки из стартового json.'''
    with open(START_LINKS, encoding='utf-8') as file:
        links = json.load(file)
    return links


def init_logging() -> None:
    '''Делаем логи.'''
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='link_spider.log',
        format='%(levelname)s: %(message)s',
        level=logging.ERROR
    )
