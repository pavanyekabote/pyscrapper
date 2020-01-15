import abc
from threading import RLock

__all__ = ['Observer', 'Observable', 'CallbackObserver']
class Observer(abc.ABC):
    """An observer, which is observed and updated / notified on change"""
    @abc.abstractmethod
    def on_url_loaded(self, url, response, **kwargs):
        """On url is loaded, or on url's http response is received"""

    def on_parse_completed(self, url, obj, **kwargs):
        """On parsing of html, as per given configuration is completed"""


class Observable(abc.ABC):
    """ An observable who holds a list of observers.
    Any concrete class implementing this interface can add / remove observers"""
    def __init__(self):
        self._observers = set()
        self._observers_lock = self._create_lock()

    @abc.abstractmethod
    def add_observer(self, observer: Observer):
        """ """

    def remove_observer(self, observer: Observer):
        """ Removes an observer from list of observers."""
        with self._observers_lock:
            if len(self._observers) > 0:
                self._observers.remove(observer)

    def _create_lock(self):
        return RLock()

class CallbackObserver(Observer):
    """ An observer which calls given list of callback methods,
        on completion of actual Observable's task"""

    def __init__(self, callbacks=None, url_callbacks=None):
        if callbacks is not None:
            assert hasattr(callbacks, '__iter__'), 'Callbacks must be a iterable list of callback methods'
        super().__init__()
        self._callback_lock = RLock()
        self._url_callback_lock = RLock()
        self._callback_list = callbacks or set()
        self._url_callback_list = url_callbacks or set()

    def on_url_loaded(self, url, response, **kwargs):
        """Calls back the callbacks when url is loaded"""
        with self._url_callback_lock:
            for callback in self._url_callback_list:
                callback(url, response, **kwargs)

    def on_parse_completed(self, url, obj, **kwargs):
        with self._callback_lock:
            for callback in self._callback_list:
                callback(url, obj, **kwargs)

    def add_callback(self, callback):
        assert hasattr(callback, '__call__'), 'The callback must be an instance of callable'
        with self._callback_lock:
            self._callback_list.append(callback)

    def add_url_callback(self, callback):
        assert hasattr(callback, '__call__'), 'The callback must be an instance of callable'
        with self._url_callback_lock:
            self._url_callback_list.append(callback)

    def remove(self, callback):
        with self._callback_lock:
            self._callback_list.remove(callback)

    def remove_url_callback(self, callback):
        with self.url_callback_lock:
            self._url_callback_list.remove(callback)