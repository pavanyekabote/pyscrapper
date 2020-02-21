class DriverPool(abc.ABC):
    def __init__(self, max_workers):
        self._q = queue.Queue()
        self._max_workers = max_workers

    @abc.abstractmethod
    def execute(self, url):
        pass

    @abc.abstractmethod
    def _create_driver(self):
        """"""

class PhantomDriverPool(DriverPool):
    """Create n drivers and gives exports each driver."""
    def __init__(self, max_workers = 3, driver_path=None, headers=None):
        super().__init__(max_workers)
        self._driver_path = driver_path
        self._headers = headers

    def execute(self, url):
        """Execute URL"""
        while self._q.qsize() < self._max_workers:
            self._q.put(self._create_driver())


    def _create_driver(self):
        def _create_driver(self):
            headers, driver_path = self._headers, self._driver_path
            for key, value in enumerate(headers):
                capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
                webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value
            return webdriver.PhantomJS(driver_path)




