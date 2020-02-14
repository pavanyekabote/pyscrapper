"""
Scrapper.py
=======================================
The core scrapping module of Pyscrapper.
"""

import signal
import os
import logging as log
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from pkg_resources import resource_filename
import json
import warnings
from .utilities import get_attr, parse_tags
from .resources.resource_manager import get_phantom_driver_path
from threading import Condition
from inspect import signature, _empty
import abc
warnings.filterwarnings("ignore", category=UserWarning, module=webdriver.__name__)


class RequestHandler:

    # Thread safety handling variables
    _lock: Condition = Condition()
    _count = 0
    MAX_WORKERS = os.cpu_count()

    @staticmethod
    def get_driver() -> WebDriver:
        driver_path = get_phantom_driver_path()
        headers = {'Accept': '*/*',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                                    AppleWebKit/537.36 (KHTML, like Gecko) \
                                    Chrome/79.0.3945.117 Safari/537.36'}

        for key, value in headers.items():
            capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
            webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value
        driver = webdriver.PhantomJS(driver_path)
        return driver


    @staticmethod
    def get_html_content(url, window_size=(1366, 784), pre_exec=None, post_exec=None):
        if pre_exec is not None:
            assert hasattr(pre_exec, '__call__'), 'pre_exec should be a callable'
        if post_exec is not None:
            assert hasattr(post_exec, '__call__'), 'post_exec should be a callable'
        soup, driver = None, None

        # Initialize lock
        RequestHandler._lock.acquire()
        if RequestHandler._count >= RequestHandler.MAX_WORKERS:
            RequestHandler._lock.wait()
        try:
            driver = RequestHandler.get_driver()
            RequestHandler._count += 1
            driver.set_window_size(*window_size)
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
        finally:
            if driver is not None:
                driver.close()

            # Lock clean up
            RequestHandler._count -= 1
            RequestHandler._lock.notify_all()
            RequestHandler._lock.release()
        return soup


class PyScrapper:
    """
    Each block of given configuration is parsed by an object of PyScrapper class.
    """

    __LIST_ITEM, __DATA = 'listItem', "data"
    __SELECTOR, __ATTR = "selector", "attr"
    __EQ, __FUNCTION = "eq", "function"
    CONST_KEYS = {__LIST_ITEM: True, __DATA: True, __SELECTOR: True,
                  __ATTR: True, __EQ: True, __FUNCTION: True }

    def __init__(self, html, config, is_list=False, name=''):
        """
        :type html: str
        :param html: html field takes the html page that needs to be scrapped

        :type config: dict
        :param config: This field takes the configuration, which tells the parser
                        * which part of html need to be taken and parsed
                        * how the parsed data has to be structured
        """
        self.is_list = is_list
        self.result = {}
        self.config = config
        self.key_name = name
        self.html, self.can_parse_next = self.__check_and_join_html(html)
        self.element_index = self.__get_index_to_select(config)

    @staticmethod
    def __check_and_join_html(html):
        """ This method helps to make a list of html as one html
        and checks if the current html can further be parsed.
        Returns html: BeautifulSoup, can_further_be_parsed : boolean"""
        can_be_parsed_next = False
        if type(html) == list:
            html = ' '.join([str(lis) for lis in html])

        if html is not None and len(html) != 0 and \
                (type(html) is BeautifulSoup or type(html)
                 is str or type(html) is Tag):

            html = html if type(html) == BeautifulSoup  \
                        else BeautifulSoup(str(html), "html.parser")
            can_be_parsed_next = True
        return html, can_be_parsed_next

    def as_text(self, soup_element):
        try:
            if get_attr(self.config, self.__ATTR) is None:
                if type(soup_element) == list and len(soup_element) > 0:
                    return [str(soup_elem.text).strip()
                            for soup_elem in soup_element if soup_elem is not None]
                else:
                    return str(soup_element.text).strip()
        except:
            pass

        return soup_element

    def __parse_configuration(self):
        """
        This method parses and grabs elements from html,
        creates relevant object(s) as per the configuration
        """
        html = self.html
        if type(self.config) == dict:
            """ check if the configuration is dict """

            if get_attr(self.config, self.__LIST_ITEM) is not None:
                result_list = self.__parse_list(html)
                self.result = result_list

            if get_attr(self.config, self.__SELECTOR) is not None:
                html = parse_tags(html, get_attr(self.config, self.__SELECTOR))
                if not self.is_list:
                    self.result = self.as_text(html[0]) if len(html) > 0 else self.as_text(html)
                else:
                    self.result = self.as_text(html)

            if get_attr(self.config, self.__ATTR) is not None:
                object_key = get_attr(self.config, self.__ATTR)
                if not self.is_list:
                    idx = self.element_index if (html is not None and self.element_index is not None
                                                 and len(html) > self.element_index) else 0
                    html = html[idx] if len(html) > 0 else html
                    html = get_attr(html, object_key)
                else:
                    html = [get_attr(obj, object_key) for obj in html] if len(html) > 0 else get_attr(html, object_key)
                self.result = html

            if get_attr(self.config, self.__EQ) is not None:
                if self.is_list or (self.result is not None and len(self.result) > 0 and type(self.result) == list):
                    self.result = self.result[self.element_index]

            if get_attr(self.config, self.__FUNCTION) is not None:
                cb = get_attr(self.config, self.__FUNCTION)
                assert hasattr(cb, '__call__'), 'function must be a callable type'
                sig = signature(cb)
                assert len(list(sig.parameters)) > 0, f'{ cb } ' \
                                                      f'function must have atleast one parameter for parsed object'
                name = list(sig.parameters)[0]
                default = sig.parameters[name].default
                if default == _empty:
                    self.result = cb(self.result)
                else:
                    kwarg = {name : self.result}
                    self.result = cb(**kwarg)

            # Parse for all keys
            keys = self.config.keys()
            for key in keys:
                if get_attr(self.CONST_KEYS, key) is None:
                    key_block = get_attr(self.config, key)
                    self.result[key] = self.__get_result_from_non_const_keys(key, key_block)

        elif type(self.config) == str:
            html = parse_tags(html, self.config, eq=self.element_index)
            res = str(html[0].text).strip() if len(html) == 1  else \
                    [str(x.text).strip() for x in html]
            self.result = res

    def __get_result_from_non_const_keys(self, key, key_block):
        """ This method works on those keys which are not a part of CONST keys  """
        res = ''
        html = self.html
        if type(key_block) == str:
            html = parse_tags(html, key_block, eq=self.element_index)
            if get_attr(self.config, self.__ATTR) is None and len(html) > 0:
                res = str(html[0].text).strip() if len(html) == 1 else \
                      [str(p.text).strip() for p in html]
        elif type(key_block) == dict:
            res = PyScrapper(self.html, key_block, name=key).get_scrapped_config()
        return res

    def __get_index_to_select(self, config) -> object:
        """ Check if there is an eq(helps to fetch particular index from list) option actively available and return
        it, else return None """

        eq_idx, eq = get_attr(config, self.__EQ), None
        if eq_idx is not None:
            if type(eq_idx) == str:
                try:
                    eq_idx = int(eq_idx)
                except:
                    pass
            eq = eq_idx if type(eq_idx) == int else None
        return eq

    def __parse_list(self, html):
        """ This method parses html and forms a list of configuration mirrored objects present in data block"""

        self.is_list = True
        # Check if DATA field is available or not
        data_value = get_attr(self.config, self.__DATA, none_if_empty=True)
        tag_parsed_html = parse_tags(html, get_attr(self.config, self.__LIST_ITEM))
        if data_value is None or len(data_value.keys()) == 0:
            result = [str(item.text).strip() for item in tag_parsed_html]
            return result

        sub_block_data = []
        if tag_parsed_html != '' or len(tag_parsed_html) >0:
            # Iterate through each data block, and run each
            # configuration on each data block.
            sub_block_data = [PyScrapper(tag_html,get_attr(self.config, self.__DATA))
                                  .get_scrapped_config()
                              for tag_html in tag_parsed_html]

        return sub_block_data

    def get_scrapped_config(self):
        """
        This method returns the parsed content
        """
        try:
            if self.can_parse_next:
                self.__parse_configuration()
        except Exception as e:
            raise PyScrapeException(e)
        return self.result


def scrape_content(url, config, to_string=False, raise_exception=True, window_size=(1366, 784), **kwargs):
    """
    Takes url, configuration as parameters,
    loads the given url in web browser, then parses the html
    as per the given configuration data.

    :type url: string
    :param url: URL of webpage to be scrapped

    :type config: dict
    :param config: configuration dictionary which describes which part of html should be scraped and
                    how it should be modelled.

    :type to_string: bool
    :param to_string: returns the scrapped and modelled json as string

    :return: parsed data
    """
    assert window_size is not None
    assert len(window_size) == 2
    assert type(window_size[0]) ==int and type(window_size[1]) == int
    assert type(config) is dict
    if len(config.keys()) == 0 :
        return None
    data = None
    try:
        html = RequestHandler.get_html_content(url, window_size=window_size, **kwargs)
        data = PyScrapper(html, config).get_scrapped_config()
        if to_string:
            data = json.dumps(data)
    except Exception as e:
        if isinstance(e,PyScrapeException):
            log.error("Error occured while scraping.",e)
            if raise_exception:
                raise e
            return data
        else:
            raise e
    return data


class PyScrapeException(Exception):
    pass
