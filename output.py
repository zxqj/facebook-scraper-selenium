import sys
import time
from datetime import datetime
import Browser
import urllib3
import json

from Json import encode


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

def make_output(resource, variant="file"):
    prelude = lambda: '[{t}]\t'.format(t=datetime.now().strftime('%m/%d %H:%M:%S'))
    def output_file(*args, **kwargs):
        kwargs["sep"]= "\n"
        global_args = [prelude(), *args]
        if type(resource) == str:
            with open(resource, "a") as f:
                print(*global_args, file=f, **kwargs)
        else:
            print(*global_args, file=resource, **kwargs)
    def output_discord(*args, **kwargs):
        http = urllib3.PoolManager()
        global_args = [prelude(), *args]
        for arg in global_args:
            http.request(
                'POST',
                resource,
                body=encode({'content': arg}),
                headers={'Content-Type': 'application/json'}
            )

    if variant == "discord":
        return output_discord
    if variant == "file":
        return output_file

    raise 'Attempted to create output of invalid type {t}'.format(t=variant)

d=dict()
d['informUser'] = make_output(sys.stdout)
d['debug'] = make_output(sys.stderr)
d['notify'] = make_output(sys.stderr)

def inform_user(*args, **kwargs):
    f = d['informUser']
    f(*args, **kwargs)

def debug(*args, **kwargs):
    f = d['debug']
    f(*args, **kwargs)

def notify(*args, **kwargs):
    f = d['notify']
    f(*args, **kwargs)

def configure(type="file", **config):
    for k, v in config.items():
        d[k] = make_output(v, type)