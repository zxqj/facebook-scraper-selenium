import time

from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException, \
    NoSuchElementException, TimeoutException

import Browser
from output import debug


class FancyDriver:
    def __init__(self, driver=None):
        if (driver == None):
            driver=Browser.get()
        self.driver = driver

    def safe_find_element_by_id(self, elem_id, browser=None):
        try:
            return self.driver.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def query_for_elements_until_present(self, xpath, failWaitSeconds=.05, timeout=60):
        starttime = time.time()
        while (True):
            if not (timeout == None) and time.time() - starttime > timeout:
                print("find element timed out: "+str(timeout))
                return None
            results = self.driver.find_elements_by_xpath(xpath)
            if results == None or len(results) == 0:
                time.sleep(failWaitSeconds)
                continue
            return results

    def query_for_element_until_present(self, xpath, failWaitSeconds=.05, timeout=60):
        return self.query_for_elements_until_present(xpath, failWaitSeconds=failWaitSeconds, timeout=timeout)[0];

    def force_interaction(self, interaction, failWaitSeconds=.05, timeout=None):
        starttime = time.time()
        while True:
            if not (timeout == None) and time.time() - starttime > timeout:
                print("element interaction timed out: "+str(timeout))
            try:
                interaction()
                return
            except ElementNotInteractableException:
                time.sleep(failWaitSeconds)
                continue
            except ElementClickInterceptedException:
                time.sleep(failWaitSeconds)
                continue

    def get(self, url):
        finishedrequest = False
        while (not finishedrequest):
            try:
                self.driver.get(url)
                finishedrequest = True
            except TimeoutException:
                debug('Request to {url} timed out.  Retrying.'.format(url=url))

    def __getattr__(self, item):
        return getattr(self.driver, item)