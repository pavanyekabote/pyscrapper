"""ScrappingDemo.py
    Here is an example on, how to use a the assembly components to
    load an url and scrape it as per the configuration."""
from pyscrapper.assembly.managers import StandardScrapeManager
from pyscrapper.assembly.observers import CallbackObserver
from pyscrapper.assembly.urlloaders import PhantomUrlLoader

url = 'https://www.msn.com/en-in/health/health-news'

list_config = {
            'listItem': ".rc-item-js",
            'data': {
                'content_link': {
                     'selector': 'a .contentlink',
                     'attr': 'href'
                },
            }
}

def callback(url, data, **kwargs):
    print(url, kwargs, data)

def fetch_msn(manager):
    manager.scrape(url, list_config)


if __name__ == '__main__':
    manager = StandardScrapeManager(PhantomUrlLoader(max_workers=10))
    manager.add_observer(CallbackObserver([callback]))
    fetch_msn(manager)

