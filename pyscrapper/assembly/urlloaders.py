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
from selenium import webdriver
import signal
from pyscrapper.resources.resource_manager import get_phantom_driver_path

__all__ = ['UrlLoader', 'BrowserLessUrlLoader', 'PhantomUrlLoader']


class UrlLoader(Observable, metaclass=abc.ABCMeta):
    """An interface which provides methods to load an url and shutdown current urlloader"""
    def __init__(self, pool, headers=None):
        super(UrlLoader, self).__init__()
        self._pool = pool
        self._pool_lock = self._create_lock()
        self._headers = headers or {'Accept': '*/*',
                                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                                                   AppleWebKit/537.36 (KHTML, like Gecko) \
                                                   Chrome/79.0.3945.117 Safari/537.36'}

    @abc.abstractmethod
    def load_url(self, url, **kwargs):
        """Loads url using any of selected pool ( ThreadPool / ProcessPool )"""

    @abc.abstractmethod
    def shutdown(self, wait=True):
        """Shuts down the UrlLoader"""


class BrowserLessUrlLoader(UrlLoader):
    """A concrete implementation of UrlLoader interface,
    which has a ThreadPoolExecutor to execute the URL requests concurrently,
    in a browser less context ( Incapable of lazy loading by javascript ).
    On URL response is received, The response is pushed to the observers: Observer it holds."""

    def __init__(self, pool=None, max_workers=None, headers=None, **kwargs):
        max_workers = max_workers or os.cpu_count() * 4
        pool = ThreadPoolExecutor(max_workers= max_workers)
        super(BrowserLessUrlLoader, self).__init__(pool, headers=headers)

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
        response = response.data.decode('utf-8') \
                  if response.status == 200 else None
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


class PhantomUrlLoader(UrlLoader):
    """A concrete implementation of UrlLoader interface,
    which has a ThreadPoolExecutor to execute the URL requests concurrently,
    in a browser based context ( capable of handling lazy loading by javascript ).
    It uses PhantomJS headless web browser to load the urls.
    On URL response is received, The response is pushed to the observers: Observer it holds."""

    def __init__(self, pool=None,driver_path=get_phantom_driver_path(), max_workers=None, headers=None, **kwargs):
        assert driver_path is not None, 'driver path cannot be None'
        assert os.path.exists(driver_path), f'driver path does not exists {driver_path}'
        max_workers = max_workers or os.cpu_count() * 2
        pool = ThreadPoolExecutor(max_workers=max_workers)
        super(PhantomUrlLoader, self).__init__(pool, headers=headers)
        self._driver_path = driver_path

    def load_url(self, url, **kwargs):
        """
        url : URL to be loaded by the url loader.
        pre_exec: This parameter takes a method/function as input and calls that method/function
                passing the selenium web driver object into it. The method/function is called before given url is loaded into the driver
        post_exec: This parameter takes a method/function as input and calls that method/function passing the selenium web driver
                object into it. The method/function is called after given url is loaded into the driver

        This feature allows developers to perform some extra operations on the web driver, by directly accessing the webdriver.
        """
        with self._observers_lock:
            if len(self._observers) == 0:
                warnings.formatwarning('',category=UserWarning, line=0, lineno=1, filename=None)
                warnings.warn('No Observer is added, make sure to add Observer before calling this method', UserWarning)

        def callback(f):
            exc, tb = (f.exception_info() if hasattr(f, 'exception_info') else
                       (f.exception(), getattr(f.exception(), '__traceback__', None)))
            if exc:
                self._load_url_error(url, exc, tb, **kwargs)
            else:
                self._load_url_success(url, f.result(),**kwargs)

        with self._pool_lock:
            future = self._pool.submit(self._wait_to_load_from_driver, url, **kwargs)
            future.add_done_callback(callback)

    def _wait_to_load_from_driver(self, url, pre_exec=None, post_exec=None, *args, **kwargs):
        if pre_exec is not None:
            assert hasattr(pre_exec, '__call__'), 'pre_exec should be a callable'
        if post_exec is not None:
            assert  hasattr(post_exec, '__call__'), 'post_exec should be a callable'
        driver = self._create_driver()
        if driver is not None:
            try:
                driver.maximize_window()
                # Call pre_exec method before executing the request
                if pre_exec is not None:
                    pre_exec(driver)
                driver.get(url)
                # call post_exec method passing driver object to it.
                if post_exec is not None:
                    post_exec(driver)
                source = driver.page_source
            finally:
                driver.service.process.send_signal(signal.SIGTERM)
                driver.quit()
            return source
        return None

    def _load_url_success(self, url, response, **kwargs):
        with self._observers_lock:
            for observer in self._observers:
                observer.on_url_loaded(url, response, **kwargs)

    def _load_url_error(self, url, exc, tb, **kwargs):
        raise Exception(url, exc, tb, kwargs)

    def _create_driver(self):
        path = self._driver_path
        if self._headers is not None:
            for key, value in self._headers.items():
                capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
                webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value
        driver = webdriver.PhantomJS(path, service_log_path=os.path.devnull)
        return driver

    def add_observer(self, observer: Observer):
        assert isinstance(observer, Observer), 'observer must be an instance of Observer'
        with self._observers_lock:
            self._observers.add(observer)

    def shutdown(self, wait=True):
        with self._pool_lock:
            self._pool.shutdown(wait)

        with self._observers_lock:
            self._observers.clear()
