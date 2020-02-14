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
        """ Add observer to observers list """

    def remove_observer(self, observer: Observer):
        """ Removes an observer from list of observers."""
        with self._observers_lock:
            if len(self._observers) > 0:
                self._observers.remove(observer)

    def _create_lock(self):
        return RLock()

class CallbackObserver(Observer):
    """ An observer which calls given list of callback methods,
        on completion of actual Observable's task
        url_callbacks=None : callback methods, which need to be called on loading of url is completed
        callbacks=None : callback methods, which need to be called on parsing is completed
        """

    def __init__(self, callbacks=None, url_callbacks=None):
        if callbacks is not None:
            assert hasattr(callbacks, '__iter__'), 'callbacks must be an iterable list of callback methods'
            callbacks = set(callbacks)

        if url_callbacks is not None:
            assert hasattr(url_callbacks, '__iter__'), 'url_callbacks must be a iterable list of callback methods'
            url_callbacks = set(url_callbacks)

        super().__init__()
        self._callback_lock = RLock()
        self._url_callback_lock = RLock()
        self._callback_list = callbacks or set()
        self._url_callback_list = url_callbacks or set()

    def on_url_loaded(self, url, response, *args, **kwargs):
        """Calls back the callbacks when url is loaded"""
        with self._url_callback_lock:
            for callback in self._url_callback_list:
                callback(url, response, *args, **kwargs)

    def on_parse_completed(self, url, obj, *args, **kwargs):
        with self._callback_lock:
            for callback in self._callback_list:
                callback(url, obj, *args, **kwargs)

    def add_callback(self, callback):
        """Add callback method to callbacks list..."""
        assert hasattr(callback, '__call__'), 'The callback must be an instance of callable'
        with self._callback_lock:
            self._callback_list.add(callback)

    def add_url_callback(self, callback):
        """Add callback method to url_callbacks list"""
        assert hasattr(callback, '__call__'), 'The callback must be an instance of callable'
        with self._url_callback_lock:
            self._url_callback_list.add(callback)

    def remove(self, callback):
        "Remove callback method from callbacks list..."
        assert callback in self._callback_list, f'removing unregistered {callback} callback'
        with self._callback_lock:
            self._callback_list.remove(callback)

    def remove_url_callback(self, callback):
        """Remove callback method from url callbacks list"""
        assert callback in self._url_callback_list, f'removing unregistered {callback} callback'
        with self._url_callback_lock:
            self._url_callback_list.remove(callback)