from logging import Logger
from bs4 import BeautifulSoup
from selenium import webdriver
from pkg_resources import resource_filename
import warnings
from .utilities import get_attr, parse_tags, normalize_parsed_dict
warnings.filterwarnings("ignore", category=UserWarning, module=webdriver.__name__)

DRIVER_PATH = resource_filename(__name__, "resources/phantomjs")
driver = webdriver.PhantomJS(DRIVER_PATH)


headers = { 'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8',
    'Cache-Control':'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
}

for key, value in enumerate(headers):
    capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
    webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value

logger = Logger("scrapper")

def get_html_content(url):
    global driver
    driver.get(url)
    html = driver.find_element_by_tag_name('body').get_attribute("innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    return soup


class PyScrapper:

    __LIST_ITEM, __DATA = 'listItem', "data"
    __SELECTOR, __ATTR = "selector", "attr"
    __EQ = "eq"

    CONST_KEYS = {__LIST_ITEM: True, __DATA: True, __SELECTOR: True,
                  __ATTR: True, __EQ: True }

    def __init__(self, html, config, is_list = False, name=''):
        self.is_list = is_list
        self.result = {}
        self.config = config
        self.key_name = name
        self.html, self.can_parse_next = self.__check_and_join_html(html)
        self.element_index = self.__get_index_to_select(config)
        # print("Config ", self.config, " Contenx" , self.can_parse_next)

    @staticmethod
    def __check_and_join_html(html):
        """ This method helps to make a list of html as one html
        and checks if the current html can further be parsed. Returns html: BeautifulSoup, can_further_be_parsed : boolean"""
        can_be_parsed_next = False
        if type(html) == list:
            html = ' '.join([str(lis) for lis in html])

        if html is not None and len(html) != 0 and (type(html) == BeautifulSoup or type(html) == str):
            html = html if type(html) == BeautifulSoup else BeautifulSoup(html, "html.parser")
            can_be_parsed_next = True
        return html, can_be_parsed_next

    def __parse_configuration(self):
        """ This method parses and grabs elements from html, creates relevant object(s) as per the configuration """

        if type(self.config) == dict:
            """ check if the configuration is dict """

            if get_attr(self.config, self.__LIST_ITEM) is not None:
                result_list = self.__parse_list(self.html)
                self.result = result_list

            if get_attr(self.config, self.__SELECTOR) is not None:
                self.html = parse_tags(self.html, get_attr(self.config, self.__SELECTOR))
                if not self.is_list:
                    self.result = self.html[0] if len(self.html) > 0 else self.html
                else:
                        self.result = self.html


            if get_attr(self.config, self.__ATTR) is not None:
                object_key = get_attr(self.config, self.__ATTR)
                if not self.is_list:
                    self.html = self.html[0] if len(self.html) > 0 else self.html
                    self.html = get_attr(self.html, object_key)
                else:
                    self.html = [get_attr(obj, object_key) for obj in self.html] if len(self.html) > 0 else self.html
                        # map(lambda obj: get_attr(obj, object_key), self.html) if len(self.html) > 0 else self.html
                self.result = self.html

            if get_attr(self.config, self.__EQ) is not None:
                if self.is_list:
                    self.result = self.result[self.element_index]

            # Parse for all keys
            keys = self.config.keys()
            for key in keys:
                if get_attr(self.CONST_KEYS, key) is None:
                    key_block = get_attr(self.config, key)
                    self.result[key] = self.__get_result_from_non_const_keys(key, key_block)

        elif type(self.config) == str:
            self.html = parse_tags(self.html, self.config)
            res = self.html[0].text if len(self.html) == 1  else \
                    [str(x.text) for x in self.html]
            self.result = res

    def __get_result_from_non_const_keys(self, key, key_block):
        """ This method works on those keys which are not a part of CONST keys  """
        res = ''
        if type(key_block) == str:
            self.html = parse_tags(self.html, key_block)
            if get_attr(self.config, self.__ATTR) is None and len(self.html) > 0:
                res = self.html[0].text if len(self.html) == 1 else \
                      [str(p.text) for p in self.html]
        elif type(key_block) == dict:
            res = PyScrapper(self.html, key_block, name=key, is_list=self.is_list).get_scrapped_config()
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
        if data_value is None:
            result = [str(item.text).strip() for item in tag_parsed_html]
            return result

        sub_blocks_dict = {}
        if tag_parsed_html != '' or len(tag_parsed_html) >0:
            sub_blocks_dict = { key : PyScrapper(tag_parsed_html, conf, name=key, is_list=self.is_list).get_scrapped_config() \
                                for key, conf in get_attr(self.config, self.__DATA).items() \
                                if get_attr(self.CONST_KEYS, key) is None }
            sub_blocks_dict = normalize_parsed_dict(sub_blocks_dict)

        return sub_blocks_dict

    def get_scrapped_config(self):
        if self.can_parse_next:
            self.__parse_configuration()
        if self.element_index is not None and self.is_list:
            if type(self.result) == list:
                print("CONFIG : ",self.config, " IDX : ",self.element_index, self.result)
                self.result = get_attr(self.result, self.element_index)
        return self.result




