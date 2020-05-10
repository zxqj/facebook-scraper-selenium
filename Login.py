import sys

from selenium.common.exceptions import NoSuchElementException

import Browser
from util import FancyDriver


def login(email, password, browser=None):
    if (browser == None):
        browser = Browser.get()
    try:
        browser.get("https://www.facebook.com")
        browser.maximize_window()

        # filling the form
        browser.find_element_by_name('email').send_keys(email)
        browser.find_element_by_name('pass').send_keys(password)

        # clicking on login button
        browser.find_element_by_id('loginbutton').click()
        # if your account uses multi factor authentication
        mfa_code_input = FancyDriver(browser).safe_find_element_by_id('approvals_code')

        if mfa_code_input is None:
            return

        mfa_code_input.send_keys(input("Enter MFA code: "))
        browser.find_element_by_id('checkpointSubmitButton').click()

        # there are so many screens asking you to verify things. Just skip them all
        while FancyDriver(browser).safe_find_element_by_id('checkpointSubmitButton') is not None:
            dont_save_browser_radio = FancyDriver(browser).safe_find_element_by_id('u_0_3')
            if dont_save_browser_radio is not None:
                dont_save_browser_radio.click()

            browser.find_element_by_id(
                'checkpointSubmitButton').click()

    except Exception as e:
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit()