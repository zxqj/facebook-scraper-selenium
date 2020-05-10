import Json

class RepresentedObject(object):
    def __init__(self, representation):
        if not (representation is None):
            representation.create_object(self)

    def to_json(self):
        return Json.encode(self)