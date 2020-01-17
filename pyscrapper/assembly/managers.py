import abc
from .urlloaders import UrlLoader
from .observers import  Observable, Observer, CallbackObserver
from pyscrapper.scrapper import PyScrapper
import uuid
from threading import RLock

__all__ = ['StandardScrapeManager']


class BaseScrapeManager(Observable, metaclass=abc.ABCMeta):
    """A scrape manager which takes in an UrlLoader instance,
     It manages takes responsibility to load all the urls and scrape them
     as per the given configuration."""

    def __init__(self, url_loader: UrlLoader):
        assert isinstance(url_loader, UrlLoader), 'Url loader must be an instance of UrlLoader Implemented classes'
        super(BaseScrapeManager, self).__init__()
        self._url_loader = url_loader
        self._scrapper = PyScrapper

    @abc.abstractmethod
    def scrape(self, url, config, **kwargs):
        """This method intakes url, configuration.
        Returns an unique id, which refers to current scrape request.
        The response of current request is pushed, into the callback methods with
        the unique id referring to the request made"""

    @abc.abstractmethod
    def shutdown(self):
        """Shuts down the current manager"""


class StandardScrapeManager(BaseScrapeManager, Observer):

    __doc__ = super.__doc__

    def __init__(self, url_loader: UrlLoader):
        assert isinstance(url_loader, UrlLoader)
        super(StandardScrapeManager, self).__init__(url_loader)
        url_loader.add_observer(self)
        self._scrape_lock = self._create_lock()
        self._id_data_map = {}

    def scrape(self, url, config, **kwargs):
        assert isinstance(url, str), 'url must be a str type'
        assert isinstance(config, dict), 'config must be dict'
        with self._scrape_lock:
            id = str(uuid.uuid4())
            self._id_data_map[id] = (url, config)
            self._url_loader.load_url(url, id=id, **kwargs)
            return id

    def shutdown(self, wait=True):
        with self._scrape_lock:
            self._id_data_map.clear()
            self._url_loader.shutdown(wait=wait)
        with self._observers_lock:
            self._observers.clear()

    def on_url_loaded(self, url, response, **kwargs):
        if 'id' in kwargs.keys():
            id = kwargs['id']
            with self._scrape_lock:
                url, config = self._id_data_map[id]
                del self._id_data_map[id]
            obj = None
            if response is not None:
                data = response
                obj = self._scrapper(data, config).get_scrapped_config()
                with self._observers_lock:
                    for observer in self._observers:
                        observer.on_parse_completed(url, obj, id=str(id))
            else:
                with self._observers_lock:
                    for observer in self._observers:
                        observer.on_parse_completed(url, {}, id=str(id))


    def on_parse_completed(self, url, obj, **kwargs):
        pass

    def add_observer(self, observer: Observer):
        assert isinstance(observer, Observer), 'observer is not an instance of Observer'
        with self._observers_lock:
            self._observers.add(observer)

    def _create_lock(self):
        return RLock()
