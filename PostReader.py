import time

import Browser
from models.Post import Post
from FancyDriver import FancyDriver


class PostReader(object):
    # Collector of recent FaceBook posts.
    # browser object is a reference to a selenium WebDriver through which
    # a user has already logged into Facebook
    def __init__(self, scrollDepth=5, delay=2, browser=None, readAll=False):
        self.depth = scrollDepth + 1
        self.delay = delay
        self.readAll = readAll
        self.rootUrl = "https://www.facebook.com/"
        # browser instance
        if (browser == None):
            self.browser = Browser.get()
        self.browser = FancyDriver(self.browser)

    def read_post(self, url=None, path=None, groupId=None, postId=None):
        if not (url is None):
            self.browser.get(url)
        elif not (path is None):
            self.browser.get(self.rootUrl+path)
        else:
            self.browser.get(self.rootURL+"groups/"+groupId+"/permalink/"+postId)
        return Post.InFeed.get(self.browser)

    def read_post_as(self, representation, url=None, path=None, groupId=None, postId=None):
        if not (url is None):
            self.browser.get(url)
        elif not (path is None):
            self.browser.get(self.rootUrl+path)
        else:
            self.browser.get(self.rootURL+"groups/"+groupId+"/permalink/"+postId)
        return representation.get(self.browser)

    def scroll_all(self):
        """A method for scrolling through all page."""

        # Get scroll height.
        last_height = self.browser.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.browser.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def read_posts(self, url):
        # navigate to page
        self.browser.get(url)

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):

            # Scroll down to bottom
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(self.delay)

        links = self.browser.find_elements_by_link_text("See more")
        for link in links:
            link.click()

        # Once the full page is loaded, we can start scraping
        return Post.InFeed.get_all(self.browser)

    def read_page_posts(self, pageName):
        return self.read_posts(self.rootUrl + pageName + '/')

    def read_group_posts(self, groupId):
        return self.read_posts(self.rootUrl + "groups/" + groupId + '/')