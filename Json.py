from json import JSONEncoder
import json

class Encoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def encode(thing):
    return json.dumps(thing, indent=4, cls=Encoder)