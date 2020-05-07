import time

import Browser
from Post import Post


class PostReader(object):
    """Collector of recent FaceBook posts.
           Note: We bypass the FaceBook-Graph-API by using a
           selenium FireFox instance!
           This is against the FB guide lines and thus not allowed.

           USE THIS FOR EDUCATIONAL PURPOSES ONLY. DO NOT ACTAULLY RUN IT.
    """

    def __init__(self, depth=5, delay=2, browser=None):
        self.depth = depth + 1
        self.delay = delay
        self.rootUrl = "https://www.facebook.com/"
        # browser instance
        if (browser == None):
            self.browser = Browser.get()


    def readPost(self, url=None, path=None, groupId=None, postId=None):
        if not (url is None):
            self.browser.get(url)
        elif not (path is None):
            self.browser.get(self.rootUrl+path)
        else:
            self.browser.get(self.rootURL+"groups/"+groupId+"/permalink/"+postId)
        return Post.InFeed.get(self.browser)

    def readPostAs(self, representation, url=None, path=None, groupId=None, postId=None):
        if not (url is None):
            self.browser.get(url)
        elif not (path is None):
            self.browser.get(self.rootUrl+path)
        else:
            self.browser.get(self.rootURL+"groups/"+groupId+"/permalink/"+postId)
        return representation.get(self.browser)

    def readPosts(self, url):
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
        return Post.InFeed.getAll(self.browser)

    def readPagePosts(self, pageName):
        return self.readPosts(self.rootUrl + pageName + '/')

    def readGroupPosts(self, groupId):
        return self.readPosts(self.rootUrl + "groups/" + groupId + '/')