"""Scrapping html list, and execute function on the parsed data."""
from pyscrapper.assembly.managers import StandardScrapeManager
from pyscrapper.assembly.observers import CallbackObserver
from pyscrapper.assembly.urlloaders import PhantomUrlLoader


# Right angular bracket ">" is used,
# to select hierarchal sub elements in html
# Eg : <div class=".header"><h1>Header</h1></div>
# To Select h1 tag value, define .header > h1
# as h1 is subelement/child of .header

# Configuration
CONFIG = {
    "articles": {
        "listItem": ".content > .article",
        "data": {
            "title": "a .article-title > h1",
            # Select the first tag ( at index 0 ) in list of tags using eq.
            "first_tag": {
                "selector": ".tags > span",
                "eq": 0
            }
        },
    }
}

URL = "https://ionicabizau.net"


def callback(url, data, **kwargs):
    """ Prints url, data, unique id which is generate while scrape request is created."""
    print('Unique Id in callback ', kwargs['id'])
    print("Result ",url, data)


if __name__ == '__main__':
    manager = StandardScrapeManager(PhantomUrlLoader(max_workers=10))
    manager.add_observer(CallbackObserver([callback]))
    id = manager.scrape(URL, CONFIG)
    print('Unique id ', id)


# Output
# Unique id  9ccc66a8-81f5-43fa-80c0-0115389519ea
# Unique Id in callback  9ccc66a8-81f5-43fa-80c0-0115389519ea
# Result  https://ionicabizau.net
#  {
#    'articles': [
#         {
#             'title': "BWV 637 — Through Adam's Fall (Bach)",
#             'first_tag': 'pipe organ'
#         },
#         {
#             'title': 'Op 148, Verset No. 2 — Louis J.-A. Lefébure-Wély',
#             'first_tag': 'pipe organ'
#         }
#           // ... truncating some part of output, due to space constraint.
#     ]
#  }
#
