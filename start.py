from datetime import datetime
from Login import login
from models.Post import Post
from models.Post import PollPost
import argparse
from Json import encode
from PollPostChangeObserver import PollPostChangeObserver
from PostReader import PostReader
from output import inform_user, debug, configure
from sys import maxsize
import conf
import dateparser

parser = argparse.ArgumentParser(description='Non API public FB miner')

def make_conf(cli_args):
    # cli_args contains set of all valid config values, some may not be set in conf
    # we want all valid config properties to *exist* on the conf module and be None
    # if they're not set, so we dont get AttributeError
    for key, val in cli_args.__dict__.items():
        if not hasattr(conf, key):
            setattr(conf, key, val)

    for key, val in cli_args.__dict__.items():
        if not (val is None):
            setattr(conf, key, val)

    return conf

parser.add_argument("-c", "--command", choices=["scrape", "watch-poll"], action="store",
                    dest="command",
                    help="What you want the script to do.  The value of this option determines the meaning of all"
                         "subsequent options."
                         ""
                         "scrape"
                         "Save posted content to specified output channel"                         
                         ""
                         "watch-poll"                         
                         "Watch a poll for user votes and report selection changes as they happen."
                         "Optionally send a notification when the poll is finished")

parser.add_argument("-p", "--post", action="store",
                    dest="post",
                    help="Url of post you want to consider")

parser.add_argument("-g", '--group', '--groups', nargs='+',
                    dest="groups",
                    help="List the URLs of groups you want to consider")

parser.add_argument('--pg', '--page', '--pages', nargs='+',
                    dest="pages",
                    help="List the URLs of pages you want to consider")

# TODO: change this 'in multiples of roughly 8' bullshit
parser.add_argument("-d", "--depth", action="store",
                    dest="depth", default=5, type=int,
                    help="How many recent posts you want to consider -- in multiples of (roughly) 8.")

## Poll-specific options
parser.add_argument("--uf", "--user-file", action="store",
                    dest="poll_user_names_file",
                    help="Text file containing a return-delimited list of poll users.  "+
                         "This should be an exhaustive list of all users expected to vote.  ")

parser.add_argument("--complete-on-quorum", action="store",
                    dest="poll_complete_on_quorum", type=bool, default=False,
                    help="Whether to consider the poll completed when all players have voted."
                         "If true, --user-file option is required")

parser.add_argument("-e", "--pd", "--poll-deadline", "--deadline", action="store",
                    dest="poll_deadline", default=None)

parser.add_argument("--notify-on-complete", action="store",
                    dest="poll_notify_on_complete", type=bool, default=False,
                    help="Whether to send a message via the notify channel when the poll has completed."
                         "This option does nothing if --complete-on-quorum is false and --user-file "
                         "is not provided.")

parser.add_argument("--notify-on-unknown-user", action="store",
                    dest="poll_notify_on_unknown_user", type=bool, default=False,
                    help="Whether to send a message via the notify channel when an unlisted user places a vote.")

parser.add_argument("--daemon-mode", action="store",
                    dest="poll_daemon_mode", type=bool, default=False,
                    help="Rechecks feed under consideration until the latest post is an open poll, at which point "
                         "it begins watching.  Note that the list of poll users is refreshed from the --user-file"
                         "when changes are made to it and --poll-deadline is parsed when a new poll is found so arguments "
                         "like 'tomorrow at 9pm' are relative to the time the poll is first discovered")

## Output and logging
#
# There are three output channels.  They're listed below in roughly the order of the importance of the messages
# they are meant to transmit, though they should really be viewed as distinct types of output with no imagined
# ordering.
#
#   log                     program trace information -- for developers
#   inform (or 'output')    program output -- for users
#   notify                  information meant to be seen by someone in a timely manner - think SMS, push notifications
#
# A globally-available function for each level is configured on start up.
# Output sent to more severe levels is NOT implicitly sent to less severe ones (in contrast to most logging
#  frameworks)

parser.add_argument("-l", "--log-file", action="store",
                    dest="log_file",
                    help="File you want to log to.  Otherwise, the default is standard error")

parser.add_argument("-o", "--output-file", action="store",
                    dest="output_file",
                    help="File you want the output to go to.  Otherwise, the default is standard out")

parser.add_argument("--ld", "--log-discord", action="store",
                    dest="log_discord",
                    help="URL of discord webhook which you would like to execute with log")

parser.add_argument("--od", "--output-discord", action="store",
                    dest="output_discord",
                    help="URL of discord webhook which you would like to execute with output")

parser.add_argument("--ed", "--notify-discord", action="store",
                    dest="notify_discord",
                    help="URL of discord webhook which you would like to execute with notify-level messages")

args = parser.parse_args()

def do_watch_poll(conf, reader, url):
    def callback(changeDescription):
        inform_user(datetime.now().strftime("%m-%d %H:%M:%S"))
        inform_user(*changeDescription)
        inform_user("")
    player_list = None
    if not (conf.poll_user_names_file is None):
        with open(conf.poll_user_names_file, "r") as f:
            player_list = [l.rstrip("\n") for l in filter(lambda l: not l[0]=='#', f.readlines())]
    if not conf.poll_deadline is None:
        poll_deadline = dateparser.parse(conf.poll_deadline)
    changeObserver = PollPostChangeObserver(0, callback, reader,
                                            url=url,
                                            player_list=player_list,
                                            deadline=poll_deadline,
                                            complete_on_quorum=conf.poll_complete_on_quorum,
                                            notify_on_complete=conf.poll_notify_on_complete)
    changeObserver.run()
    exit()

def run(conf):
    email = conf.facebook_login_email
    password = conf.facebook_login_password
    if email == "" or password == "":
        print(
            "Your email or password is missing. These must both be in conf.py")
        exit()
    reader = PostReader(scrollDepth=conf.depth)
    debug('logging in')
    login(email, password)
    posts = []
    command = conf.command
    if command == "watch-poll":
        if conf.post is None and len(conf.groups) == 0:
            parser.error("--post or --group option must be provided for watch-poll command")
            return
        url = conf.post if not (conf.post is None) else conf.groups[0]
        while (True):
            debug('reading post')
            post_rep = reader.read_post_as(PollPost.PostInFeed, url=url)
            if post_rep.is_poll():
                debug('post contains poll')
                if post_rep.is_open():
                    debug('post poll is open')
                    do_watch_poll(conf, reader, url)
    elif not (conf.post is None):
        posts.append(Post(reader.read_post(conf.post)))
    else:
        if conf.groups:
            for groupId in conf.groups:
                posts.extend([Post(rep) for rep in reader.read_group_posts(groupId)])
        if conf.pages:
            for pageName in conf.pages:
                posts.extend([Post(rep) for rep in reader.read_page_posts(pageName)])

    inform_user(encode(posts))
if __name__ == "__main__":
    conf = make_conf(args)
    if conf.output_discord:
        configure(informUser=conf.output_discord, type="discord")
    elif conf.output_file:
        configure(informUser=conf.output_file)
    if conf.log_discord:
        configure(debug=conf.log_discord, type="discord")
    elif conf.log_file:
        configure(debug=conf.log_file)
    run(conf)