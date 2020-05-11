from datetime import datetime
from Login import login
from models.Post import Post
from models.Post import PollPost
import argparse
from Json import encode
from PollPostChangeObserver import PollPostChangeObserver
from PostReader import PostReader
from conf import LOGIN_PASSWORD, LOGIN_EMAIL
from output import inform_user, debug, configure

parser = argparse.ArgumentParser(description='Non API public FB miner')

parser.add_argument('-a', '--pages', nargs='+',
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

parser.add_argument("-p", "--pollPostUrl", action="store",
                    dest="pollPostUrl",
                    help="Url of a single post containing a poll")

parser.add_argument("-m", "--monitorPollPost", action="store",
                    dest="monitorPollPostUrl",
                    help="Url of single post containing a poll, which you want to monitor")

parser.add_argument("-o", "--outputFile", action="store",
                    dest="outputFile",
                    help="File you want the output to go to.  Otherwise, the default is standard out")

parser.add_argument("-l", "--logFile", action="store",
                    dest="logFile",
                    help="File you want to log to.  Otherwise, the default is standard error")

args = parser.parse_args()

def run(args, email, password):
    debug([args, email, password])
    if email == "" or password == "":
        print(
            "Your email or password is missing. These must both be in conf.py")
        exit()
    reader = PostReader(scrollDepth=args.depth)
    login(email, password)
    posts = []

    if args.monitorPollPostUrl:
        postRep = reader.read_post_as(PollPost.PostInFeed, url=args.monitorPollPostUrl)
        def callback(changeDescription):
            inform_user(datetime.now().strftime("%m-%d %H:%M:%S"))
            inform_user(*changeDescription)
            inform_user("")
        changeObserver = PollPostChangeObserver(0, callback, reader, args.monitorPollPostUrl)
        changeObserver.run()
        exit()
    elif args.pollPostUrl:
        postRep = reader.read_post_as(PollPost.PostInFeed, url=args.pollPostUrl)
        pollPost = PollPost(postRep)
        posts.append(pollPost)
    elif args.postUrl:
        posts.append(Post(reader.read_post(args.postUrl)))
    else:
        if args.groups:
            for groupId in args.groups:
                posts.extend([Post(rep) for rep in reader.read_group_posts(groupId)])
        if args.pages:
            for pageName in args.pages:
                posts.extend([Post(rep) for rep in reader.read_page_posts(pageName)])

    inform_user(encode(posts))
if __name__ == "__main__":
    if (args.outputFile):
        configure(informUser=args.outputFile)
    if (args.logFile):
        configure(debug=args.logFile)
    run(args, LOGIN_EMAIL, LOGIN_PASSWORD)