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
            }
        }
    }
}

URL = "https://ionicabizau.net"


def callback(url, data, **kwargs):
    print('Unique Id in callback ', kwargs['id'])
    print("Result ",url, data)


if __name__ == "__main__":
    manager = StandardScrapeManager(PhantomUrlLoader(max_workers=10))
    manager.add_observer(CallbackObserver([callback]))
    id = manager.scrape(URL, LIST_CONFIG)
    print('Unique id: ', id)

# // Output
# Unique id: 1f410b0a-540b-4867-9e8b-cccf1ce94738
# Unique Id in callback  1f410b0a-540b-4867-9e8b-cccf1ce94738
# Result  https://ionicabizau.net 
# {
#   "pages": [
#     {
#       "title": "Blog",
#       "url": "/"
#     },
#     {
#       "title": "About",
#       "url": "/about"
#     },
#     {
#       "title": "FAQ",
#       "url": "/faq"
#     }
#     // ... truncating some part of output, due to space constraint.
#   ]
# }
