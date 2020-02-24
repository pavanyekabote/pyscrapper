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
LIST_CONFIG = {
    "pages": {
        "listItem": "li .page",
        "data": {
            "title": "a",
            "url": {
                "selector": "a",
                "attr": "href"
            },
            "title_length":  {
                "selector": "a",
                "function": lambda title: len(title)
            }
        },
    }
}

URL = "https://ionicabizau.net"


def callback(url, data, **kwargs):
    print('Unique Id in callback ', kwargs['id'])
    print("Result ", url, data)
    

if __name__ == "__main__":
    manager = StandardScrapeManager(PhantomUrlLoader(max_workers=10))
    manager.add_observer(CallbackObserver([callback]))
    id = manager.scrape(URL, LIST_CONFIG)
    print('Unique id: ', id)

# // Output
# Unique id:  366cfa63-5c5b-4afe-ac2d-45cae2769862
# Unique Id in callback  366cfa63-5c5b-4afe-ac2d-45cae2769862
# Result  https://ionicabizau.net 
# {
#   "pages": [
#     {
#       "title": "Blog",
#       "url": "/",
#       "title_length": 4
#     },
#     {
#       "title": "About",
#       "url": "/about"
#       "title_length": 5
#     },
#     {
#       "title": "FAQ",
#       "url": "/faq"
#       "title_length": 3
#     }
#     // ... truncating some part of output, due to space constraint.
#   ]
# }
