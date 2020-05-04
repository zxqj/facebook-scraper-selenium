import json

class RepresentedObject(object):
    def __init__(self, representation):
        if not (representation is None):
            representation.createObject(self)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)