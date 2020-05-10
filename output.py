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
        kwargs["sep"]= "\n"
        global_args = [prelude, *args]
        if type(resource) == str:
            with open(resource, "a") as f:
                print(*global_args, file=f, **kwargs)
        else:
            print(*global_args, file=resource, **kwargs)
    return output

d=dict()
d['informUser'] = make_output(sys.stdout)
d['debug'] = make_output(sys.stderr)

def inform_user(*args, **kwargs):
    f = d['informUser']
    f(*args, **kwargs)

def debug(*args, **kwargs):
    f = d['debug']
    f(*args, **kwargs)

def configure(**config):
    for k, v in config.items():
        d[k] = make_output(v)
    print(d)