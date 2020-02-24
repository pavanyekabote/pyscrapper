"""ScrappingDemo.py
    Here is an example on, how to use a the assembly components to
    load an url and scrape it as per the configuration."""
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
    "title": ".header > h1",
    "desc": ".header > h2",
    "avatar": {
        "selector": ".header > img",
        "attr": "src"
    }
}
# URL of the webpage to be scrapped
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


# // Output:
#
# Unique id: 2dd4deec-8453-4485-a21d-b4911bce8abf
# Unique Id in callback  2dd4deec-8453-4485-a21d-b4911bce8abf
# Result https://ionicabizau.net
# {
#   "title": "Ionică Bizău",
#   "desc": "Programmer,  Pianist,  Jesus follower",
#   "avatar": "/@/bloggify/public/images/logo.png"
# }
#
