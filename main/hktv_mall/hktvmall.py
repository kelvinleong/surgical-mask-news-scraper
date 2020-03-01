from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "/Users/kelvinleung/Downloads/chromedriver"
HKTV_MALL = "https://www.hktvmall.com/"
ADD_TO_CART = "//*[@id='mainWrapper']/div/div[2]/div[1]/div[2]/div[3]/div[1]/button"
# LOGIN = "//*[@id='header']/div[4]/div/div[3]/a[1]"
LOGIN = "//*[@id='header']/div[5]/div/div[3]/a[1]"
FB_LOGIN = "//*[@id='command']/button"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'


def main():
    # Create a new instance of the Firefox driver
    options = Options()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": user_agent}})

    driver.get(HKTV_MALL)
    driver.save_screenshot('/Users/kelvinleung/PycharmProjects/mask-retriever/pages/hktv.png')

    try:
        login = driver.find_element_by_xpath(LOGIN)
        login.click()
        fb = driver.find_element_by_xpath(FB_LOGIN)
        fb.click()
        sleep(1)
    except Exception as e:
        print("failed to login")

    while True:
        try:
            icon = driver.find_element_by_xpath(ADD_TO_CART)
            icon.click()
        except Exception as e:
            print("loading issue.")
        driver.refresh()
        sleep(1)


if __name__ == "__main__":
    main()