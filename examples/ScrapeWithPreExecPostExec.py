"""
Scraping Demo with pre_exec, post_exec features
"""

from pyscrapper.assembly.managers import StandardScrapeManager
from pyscrapper.assembly.observers import CallbackObserver
from pyscrapper.assembly.urlloaders import PhantomUrlLoader

from selenium.webdriver.support import ui, expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json

URL = 'https://www.fandango.com/san-francisco_ca_movietimes'

# Right angular bracket ">" is used,
# to select hierarchal sub elements in html
# Eg : <div class=".header"><h1>Header</h1></div>
# To Select h1 tag value, define .header > h1
# as h1 is subelement/child of .header
CONFIG = {
    'listItem': 'li .fd-theater',
    'data': {
        'theater_id': {
            'selector': 'li .fd-theater',
            'attr': 'data-theater-id'
        },
        'theater_title': {
            'selector': 'div .fd-theater__header > div .fd-theater__name-wrap > h3 .fd-theater__name > a',
            'eq': 0
        }
    }
}


# callback method, for parsed result
def callback(url, data, **kwargs):
    print('Result is ', data)


# There are some websites like fandango.com, which takes a lot of time to load
# the content on the browser. By default, the browser gives back
# the html response after a little load time.
# But what if we want to wait until some element is loaded on the html page?
# Here comes the solution for that, use pre_exec, post _exec parameters
# pre_exec: A callback function which accepts one parameter,
#           which is the selenium webdriver. This gets called before the url is loaded
#           in the web driver/ web browser
#
# post_exec : A callback function which accepts one parameter,
#            which is the selenium webdriver. This gets called after the url is loaded
#            in the web driver/ web browser
#


# Callback method for post_exec, which accepts one parameter, which is the selenium driver
def wait_for_elements_to_load(driver) -> None:
    """ Make the driver wait until the CSS Selector .fd-theater__header is visible in html,
    if not loaded, then exit the driver in 40 (timeout) seconds"""
    try:
        timeout = 40
        ui.WebDriverWait(driver, timeout)\
            .until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'fd-theater__header')))
    except TimeoutException:
        pass


if __name__ == '__main__':
    manager = StandardScrapeManager(PhantomUrlLoader(max_workers=10))
    manager.add_observer(CallbackObserver([callback]))

    # Setting wait_for_elements_to_load as post_exec parameter,
    # Once the driver loads url, then the post_exec's method i.e, wait_for_elements_to_load
    # method is called.
    id = manager.scrape(URL, CONFIG, post_exec=wait_for_elements_to_load)

    # Similarly you can assign pre_exec with a callback method,
    # in which you can directly access the web driver and
    # perform any operation on it.


# output
# Result
# [
#     {
#         "theater_id": "AADAS",
#         "theater_title": "AMC Kabuki 8"
#     },
#     {
#         "theater_id": "AAUDV",
#         "theater_title": "Century San Francisco Centre 9 and XD"
#     },
#     {
#         "theater_id": "AANEM",
#         "theater_title": "AMC Metreon 16"
#     },
#     {
#         "theater_id": "AAFBR",
#         "theater_title": "Roxie Theater"
#     },
#     {
#         "theater_id": "AADDS",
#         "theater_title": "Opera Plaza Cinema"
#     },
#     {
#         "theater_id": "AAUZJ",
#         "theater_title": "Yerba Buena Center for the Arts"
#     },
#     {
#         "theater_id": "AADDH",
#         "theater_title": "Clay Theatre"
#     },
#     {
#         "theater_id": "AAYFX",
#         "theater_title": "SFMOMA - Phyllis Wattis Theater"
#     },
#     {
#         "theater_id": "AAUSM",
#         "theater_title": "San Francisco Museum of Modern Art"
#     },
#     {
#         "theater_id": "AAFBO",
#         "theater_title": "Castro Theatre"
#     }
# ]

