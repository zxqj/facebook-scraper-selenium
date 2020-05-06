import Json

class RepresentedObject(object):
    def __init__(self, representation):
        if not (representation is None):
            representation.createObject(self)

    def toJson(self):
        return Json.encode(self)