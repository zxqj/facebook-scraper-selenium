from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from Post import Post
import sys
import time
import argparse
import csv
import calendar

parser = argparse.ArgumentParser(description='Non API public FB miner')

parser.add_argument('-p', '--pages', nargs='+',
                    dest="pages",
                    help="List the pages you want to scrape for recent posts")

parser.add_argument("-g", '--groups', nargs='+',
                    dest="groups",
                    help="List the groups you want to scrape for recent posts")

parser.add_argument("-d", "--depth", action="store",
                    dest="depth", default=5, type=int,
                    help="How many recent posts you want to gather -- in multiples of (roughly) 8.")

parser.add_argument("-u", "--postUrl", action="store",
                    dest="postUrl",
                    help="Url of single post")
args = parser.parse_args()

BROWSER_EXE = '/Applications/Firefox.app/Contents/MacOS/firefox-bin'
GECKODRIVER = '/usr/local/bin/geckodriver'

FIREFOX_BINARY = FirefoxBinary(BROWSER_EXE)

#  Code to disable notifications pop up of Chrome Browser

PROFILE = webdriver.FirefoxProfile()
# PROFILE.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
PROFILE.set_preference("dom.webnotifications.enabled", False)
PROFILE.set_preference("app.update.enabled", False)
PROFILE.update_preferences()

class PostReader(object):
    """Collector of recent FaceBook posts.
           Note: We bypass the FaceBook-Graph-API by using a 
           selenium FireFox instance! 
           This is against the FB guide lines and thus not allowed.

           USE THIS FOR EDUCATIONAL PURPOSES ONLY. DO NOT ACTAULLY RUN IT.
    """

    def __init__(self, depth=5, delay=2):
        self.depth = depth + 1
        self.delay = delay
        self.rootUrl = "https://www.facebook.com/"
        # browser instance
        self.browser = webdriver.Firefox(executable_path=GECKODRIVER,
                                         firefox_binary=FIREFOX_BINARY,
                                         firefox_profile=PROFILE,)

    def readPost(self, url=None, path=None, groupId=None, postId=None):
        if not (url is None):
            self.browser.get(url)
        elif not (path is None):
            self.browser.get(self.rootUrl+path)
        else:
            self.browser.get(self.rootURL+"groups/"+groupId+"/permalink/"+postId)
        return Post.inFeed.get(self.browser)


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

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)

            # clicking on login button
            self.browser.find_element_by_id('loginbutton').click()
            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element_by_id('checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element_by_id(
                    'checkpointSubmitButton').click()

        except Exception as e:
            print("There's some error in log in.")
            print(sys.exc_info()[0])
            exit()

# Once the full page is loaded, we can start scraping
def postsToCsvFile(posts, filePath):
    # creating CSV header
    with open(filePath, "w", newline='', encoding="utf-8") as save_file:
        writer = csv.writer(save_file)
        writer.writerow(["Author", "uTime", "Text"])
        for post in posts:
            writer.writerow([post.user.name, post.time, post.status])

if __name__ == "__main__":

    with open('credentials.txt') as f:
        email = f.readline().split('"')[1]
        password = f.readline().split('"')[1]

        if email == "" or password == "":
            print(
                "Your email or password is missing. Kindly write them in credentials.txt")
            exit()
    reader = PostReader(depth=args.depth)
    reader.login(email, password)
    posts = []
    if args.postUrl:
        posts.append(reader.getPost(args.postUrl))
    else:
        if args.groups:
            for groupId in args.groups:
                posts.extend([Post(rep) for rep in reader.readGroupPosts(groupId)])
        if args.pages:
            for pageName in args.pages:
                posts.extend([Post(rep) for rep in reader.readPagePosts(pageName)])

    postsToCsvFile(posts,"posts.csv")