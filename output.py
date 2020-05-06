import sys
import time
from datetime import datetime

from Browser import Browser


def std_out(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def std_error(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)

def debug(*args):
    prelude='[{t}]\t'.format(t=datetime.now().strftime('%m/%d %H:%M:%S'))
    std_error(*[prelude, *args], sep="\n")

def informUser(*args):
    std_out(*args, sep="\n")

def log_exceptions(f):
    def logger_wrap(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except:
            debug("Unexpected error:", sys.exc_info()[0])
            Browser.get().save_screenshot("error_"+str(time.time())+".png")
            raise
    return logger_wrap
