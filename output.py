import sys
import time
from datetime import datetime
import Browser

class decorators:
    def log_exceptions(f):
        def logger_wrap(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except:
                debug("Unexpected error:", sys.exc_info()[0])
                Browser.get().save_screenshot("error_" + str(time.time()) + ".png")
                raise

        return logger_wrap

def make_output(resource):
    def output(*args, **kwargs):
        prelude = '[{t}]\t'.format(t=datetime.now().strftime('%m/%d %H:%M:%S'))
        kwargs.update("sep", "\n")
        global_args = [prelude, *args]
        if type(resource) == "str":
            with open(resource, "a") as f:
                print(*global_args, file=f, **kwargs)
        else:
            print(*global_args, file=resource, **kwargs)
    return output

def informUser(*args, **kwargs):
    make_output(sys.stdout)(*args, **kwargs)

def debug(*args, **kwargs):
    make_output(sys.stderr)(*args, **kwargs)

def configure(**config):
    for k, v in config:
        globals()[k] = make_output(v)