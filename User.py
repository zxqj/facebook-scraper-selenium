from RepresentedObject import RepresentedObject
from Representation import Representation

class CirclePictureRep(Representation):

    def __init__(self, node):
        super().__init__(node)

    def createObject(self, dataObj):
        dataObj.name = self.node.text

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, CirclePictureRep)

    @staticmethod
    def getAll(rootNode):
        nodes = rootNode.find_elements_by_xpath(".//a[@data-hovercard-referer]")
        return [CirclePictureRep(node) for node in nodes]

# we will try to implement this so that a user object can be created 
# from the different kinds of nodes that indicate a user is there
# there's the circle picture, sometimes just a link containing their name,
# sometimes both
class User(RepresentedObject):
    CirclePicture = CirclePictureRep
    def __init__(self, rep):
        super().__init__(rep)