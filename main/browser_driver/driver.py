from selenium import webdriver
from selenium.webdriver.chrome.options import Options

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/35.0.1916.47 Safari/537.36 '

chrome_driver_path = "/Users/kelvinleung/Downloads/chromedriver"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Driver(metaclass=Singleton):
    _driver = None

    def check_and_get(self):
        if self._driver is None:
            options = Options()
            options.add_argument("start-maximized")
            options.add_argument("--headless")
            options.add_experimental_option("excludeSwitches", ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)

            self._driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)
            self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                                       Object.defineProperty(navigator, 'webdriver', {
                                         get: () => undefined
                                       })
                                     """
            })
            self._driver.execute_cdp_cmd("Network.enable", {})
            self._driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": user_agent}})
        return self._driver

    @property
    def driver(self):
        return self.check_and_get()


