from logging import Logger
from bs4 import BeautifulSoup
from selenium import webdriver
from pkg_resources import  resource_filename
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module=webdriver.__name__)

DRIVER_PATH =  resource_filename(__name__,"resources/phantomjs")
driver = webdriver.PhantomJS(DRIVER_PATH)
logger = Logger("scrapper")

def getHtmlContent(url):
    global driver
    driver.get(url)
    html = driver.find_element_by_tag_name('body').get_attribute("innerHTML")
    content = ""
    try:
        content = html;
    except:
        content = ""
    # f = open("file.html", "w")
    # f.write(html)
    # f.close()
    soup = BeautifulSoup(content, "html.parser")
    return soup

class BlockHolder:
    LIST_ITEM = 'listItem'
    DATA = 'data'
    SELECTOR = 'selector'
    ATTR = 'attr'
    EQ = "eq"
    WHICH = "which"
    const_keys = [LIST_ITEM, DATA, SELECTOR, ATTR, EQ, WHICH]

    def __init__(self, html, config, isFirst=False, isList=False, name=''):
        self.is_parent = False
        self.children = []
        self.obj_parent = None
        self.isList = isList
        print(name, "HTML TYPE : ", type(html), "Config ==> ", config)
        #         if(type(html) == ResultSet):
        #             print("Resultset : ",html)
        self.config = config
        self.isFirst = isFirst
        self.obj_name = name
        self.fObj = {}
        if type(html) == list:
            html = ' '.join([str(lis) for lis in html])
        if html != None and len(html) != 0 and (type(html) == BeautifulSoup or type(html) == str):
            self.html = html if type(html) == BeautifulSoup else BeautifulSoup(html, "html.parser")
            self.__parse_config()

    def name(self, name):
        self.obj_name = name
        return self

    def parent(self, parent):
        self.obj_parent = parent
        return self

    def __parse_config(self):
        mWhich = self.__get_attr(self.config, self.WHICH)
        mWhich = mWhich - 1 if mWhich != None and type(mWhich) == int else None
        if type(self.config) == dict:

            mhtml = self.html
            keys = self.config.keys()
            if not self.isFirst:
                if self.LIST_ITEM in keys:

                    self.isParent = True
                    self.isList = True
                    print("MWHICH ",mWhich)
                    # If no data block i.e, no keys available in data, nothing can be selected
                    if self.__get_attr(self.config, self.DATA) == None:
                        self.fObj = [item for item in self.__parse_tags(mhtml, self.__get_attr(self.config, self.LIST_ITEM))]
                        if mWhich is not None:
                            final_which= self.__get_attr(self.fObj, mWhich)
                            self.fObj = final_which if  final_which != None else ''
                        return


                    childHtml = self.__parse_tags(mhtml, self.__get_attr(self.config, self.LIST_ITEM))
                    if childHtml != '' or len(childHtml) > 0:
                        obs = [{child_key: child_config} for child_key, child_config in self.config[self.DATA].items() ]
                        self.children = {child_key:
                                             BlockHolder(childHtml, child_config, name=child_key, isList=True).name(
                                                 child_key).parent(
                                                 self).parsed_data() \
                                         for child_key, child_config in self.config[self.DATA].items() if child_key not in self.const_keys}
                        print("CHILDREN : ", self.children)
                        self.fObj = self.normalize(self.children)
                        if mWhich is not None:
                            print("After children ... ", mWhich, self.__get_attr(self.config, self.WHICH))
                            final_which= self.__get_attr(self.fObj, mWhich)
                            self.fObj = final_which if  final_which != None else ''
                if self.SELECTOR in keys:
                    tag = self.config[self.SELECTOR]
                    print("Selector : ", tag)
                    mhtml = self.__parse_tags(mhtml, tag)
                    if not self.isList:
                        self.fObj = mhtml[0] if len(mhtml) > 0 else mhtml
                    else:
                        self.fObj = mhtml

                if self.ATTR in keys:
                    k = self.config[self.ATTR]
                    if not self.isList:
                        mhtml = mhtml[0] if len(mhtml) > 0 else mhtml
                        mhtml = self.__get_attr(mhtml, k)
                    else:
                        mhtml = [self.__get_attr(mhtm, k) for mhtm in mhtml] if len(mhtml) > 0 else mhtml
                    self.fObj = mhtml

                for key in keys:
                    if key not in self.const_keys:
                        data_block = self.__get_attr(self.config, key)
                        # If key's value is a string which means it is a selector, then just parse the selector and  set data.
                        if type(data_block) == str:
                            parsed_data = self.__parse_tags(mhtml, data_block)
                            if self.ATTR not in keys and len(parsed_data) > 0:
                                self.fObj[key] = parsed_data[0].text if len(parsed_data) == 1 else \
                                    [str(p.text) for p in parsed_data]


                        elif type(data_block) == dict:
                            print(self.isList, "DBLOCK ", data_block)
                            block = BlockHolder(mhtml, data_block, name=key, isList=self.isList).name(key).parent(self)
                            self.fObj[key] = block.parsed_data()
        elif type(self.config) == str:
            parsed_data = self.__parse_tags(self.html, self.config)
            self.fObj = parsed_data[0].text if len(parsed_data) == 1 else \
                [str(p.text) for p in parsed_data]
            if mWhich is not None:
                final_which = self.__get_attr(self.fObj, mWhich)
                self.fObj = final_which if final_which != None else ''

    def parsed_data(self):
        return self.fObj

    def normalize(self, indict):
        arr = []
        index = 0
        size = max([len(vals) for vals in indict.values()])
        # size = len(next(iter(indict.values())))
        while index < size:
            mObj = {}
            for k, v in indict.items():
                try:
                    mObj[k] = str(v[index]).strip()
                except:
                    mObj[k] = ''
            arr.append(mObj)
            index += 1
        return arr

    def __get_attr(self, obj, key):
        #         print(obj, key)
        try:
            return obj[key]
        except:
            return None

    # Parses html selector tags to soup searchable tags
    # Eg :  #source-person >  div .name
    # The above eg is parsed to [ soup.select('#source-person'), soup.find_all('div', {'class' : "name"}) ] which will be
    # serially executed on each one's result

    def __parse_tags(self, mhtml, tags):
        if mhtml == None:
            return []
        html = mhtml
        childs = tags.split(">")
        #         print("Length : ",len(childs), childs)
        # For each of tag group : [ video #source-person, div .name ]
        for child in childs:
            mClass, mId, mSelector = [], None, None

            # For each of tag in [video, #source-person]
            for label in child.split():
                #                 print("Label : ",label)
                # If tag starts with . => consider it as class
                if label.startswith("."):
                    mClass.append(label)

                # If tag startsWith # => consider it as (unique) id
                elif label.startswith("#"):
                    if mId is not None:
                        raise Exception("Cannot have multiple id's at block " + str(child) + " in " + str(tags))
                    mId = label

                # Else consider the tag as a selector i.e, an html tag
                else:
                    if mSelector is not None:
                        raise Exception("Cannot have multiple selectors at block " + str(child) + " in " + str(tags))
                    mSelector = label
            if (self.obj_name == 'name'):
                print(" VARS: ", mId, mSelector, mClass, html)

            #             print("Parsing for ",(mId, mSelector, mClass))
            # End of parsing label
            # if id is not none; then find directly with id. No need of any other selectors
            if mId is not None:
                if type(html) == BeautifulSoup:
                    html = [htm for htm in html.select(mId)]
                else:
                    html = [item for htm in html for item in htm.select(mId)]


            # If selector is not none and class is present then
            # html.find_all('div', {'class' : 'name person'})
            elif mSelector != None and len(mClass) > 0:
                attrs = {"class": ' '.join([cls[1:] for cls in mClass])}
                if type(html) == BeautifulSoup:
                    html = [htm for htm in html.find_all(mSelector, attrs)]
                else:
                    html = [item for htm in html for item in htm.find_all(mSelector, attrs)]

            # If mSelector is not available and only mClasses are available, then select all elements with those classes
            # html.select('.name.person')
            elif mSelector == None and len(mClass) > 0:
                clsparam = ''.join(mClass)
                if type(html) == BeautifulSoup:
                    html = [htm for htm in html.select(clsparam)]
                else:
                    html = [item for htm in html for item in htm.select(clsparam)]
            elif mSelector != None and len(mClass) == 0 and mId == None:
                if type(html) == BeautifulSoup:
                    html = [htm for htm in html.find_all(mSelector)]
                else:
                    html = [item for htm in html for item in htm.find_all(mSelector)]
        if self.obj_name == 'name':
            print("Returning HTML ", html)
        return html

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.obj_name) + " => " + str(self.config) + " ==> " + str(self.fObj)


