import abc
from .observers import Observable, Observer
from urllib3 import PoolManager
import  queue
from concurrent.futures import ThreadPoolExecutor, Future, ProcessPoolExecutor
from threading import Thread, RLock
from pyscrapper.scrapper import PyScrapper
import abc
import six
import time
from datetime import datetime
import os
import warnings

__all__ = ['UrlLoader', 'BrowserLessUrlLoader']


class UrlLoader(Observable, metaclass=abc.ABCMeta):
    """An interface which provides methods to load an url and shutdown current urlloader"""
    def __int__(self, pool):
        super(UrlLoader, self).__init__()
        self._pool = pool
        self._pool_lock = self._create_lock()

    @abc.abstractmethod
    def load_url(self, url, **kwargs):
        """Loads url using any of selected pool ( ThreadPool / ProcessPool )"""

    @abc.abstractmethod
    def shutdown(self, wait=True):
        """Shuts down the UrlLoader"""


class BrowserLessUrlLoader(UrlLoader):
    """A concrete implementation of UrlLoader interface,
    which has a ThreadPoolExecutor to execute the URL requests concurrently.
    On URL response is received, The response is pushed to the observers: Observer it holds."""

    def __init__(self, max_workers=None, headers=None):
        max_workers = max_workers or os.cpu_count() * 4
        pool = ThreadPoolExecutor(max_workers= max_workers)
        super(BrowserLessUrlLoader, self).__int__(pool)
        self._headers = headers or {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                                    AppleWebKit/537.36 (KHTML, like Gecko) \
                                    Chrome/48.0.2564.116 Safari/537.36'}

    def load_url(self, url, **kwargs):
        """Load the given url as http request and push response to observers"""
        with self._observers_lock:
            if len(self._observers) == 0:
                warnings.formatwarning('',
                                       category=UserWarning, line=0, lineno=1, filename=None)
                warnings.warn('No Observer is added, make sure to add Observer before calling this method', UserWarning)

        def callback(f):
            exc, tb = (f.exception_info() if hasattr(f, 'exception_info') else
                       (f.exception(), getattr(f.exception(), '__traceback__', None)))
            if exc:
                self._load_url_error(url, exc, tb, **kwargs)
            else:
                self._load_url_success(url, f.result(), **kwargs)

        with self._pool_lock:
            future = self._pool.submit(PoolManager().request,'GET', url, headers=self._headers)
            future.add_done_callback(callback)

    def _load_url_success(self, url, response, **kwargs):
        with self._observers_lock:
            for observer in self._observers:
                observer.on_url_loaded(url, response, **kwargs)

    def _load_url_error(self, url, exc, tb, **kwargs):
        raise Exception(url, exc, tb, kwargs)

    def add_observer(self, observer: Observer):
        assert isinstance(observer, Observer), 'observer must be an instance of Observer'
        with self._observers_lock:
            self._observers.add(observer)

    def shutdown(self, wait=True):
        with self._pool_lock:
            self._pool.shutdown(wait)

        with self._observers_lock:
            self._observers.clear()

