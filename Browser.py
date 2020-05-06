from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from conf import BROWSER_EXE,GECKODRIVER
FIREFOX_BINARY = FirefoxBinary(BROWSER_EXE)

class Browser:
    inst = None

def get():
    if (Browser.inst is None):
        PROFILE = webdriver.FirefoxProfile()
        # PROFILE.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
        PROFILE.set_preference("dom.webnotifications.enabled", False)
        PROFILE.set_preference("app.update.enabled", False)
        PROFILE.update_preferences()
        firefoxOptions = webdriver.FirefoxOptions()
        firefoxOptions.headless = True
        firefoxOptions.add_argument("--width=1920`")
        firefoxOptions.add_argument("--height=1080")
        Browser.inst = webdriver.Firefox(executable_path=GECKODRIVER,
                                         firefox_binary=FIREFOX_BINARY,
                                         firefox_profile=PROFILE,
                                         firefox_options=firefoxOptions)
    return Browser.inst

def getDialogNode():
    browser = get()
    return browser.find_elements_by_xpath(".//div[contains(@class,'profileBrowserDialog')]")[0]