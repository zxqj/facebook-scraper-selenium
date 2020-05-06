from RepresentedObject import RepresentedObject
from Representation import Representation

class TextLinkRep(Representation):

    def __init__(self, node):
        super().__init__(node)

    def createObject(self, dataObj):
        dataObj.name = self.node.text

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, TextLinkRep)

    @staticmethod
    def getAll(rootNode):
        nodes = rootNode.find_elements_by_xpath(".//a[@data-hovercard][child::text()]")
        return [TextLinkRep(node) for node in nodes]

class CirclePictureRep(Representation):

    def __init__(self, node):
        super().__init__(node)

    def createObject(self, dataObj):
        # username set on aria-label attribute of small pictures next to polls
        maybeName = self.node.get_attribute('aria-label')
        if (maybeName is None):
            # username set on aria-label of img element inside of a tag for post-heading user pic and sidebar user pics
            imgNodes = self.node.find_elements_by_xpath("./img[@aria-label]")
            maybeName = imgNodes[0].get_attribute('aria-label')
        dataObj.name = maybeName

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, CirclePictureRep)

    @staticmethod
    def getAll(rootNode):
        nodes = rootNode.find_elements_by_xpath(".//a[@data-hovercard][child::img]")
        return [CirclePictureRep(node) for node in nodes]


# we will try to implement this so that a user object can be created 
# from the different kinds of nodes that indicate a user is there
# there's the circle picture, sometimes just a link containing their name,
# sometimes both
class User(RepresentedObject):
    CirclePicture = CirclePictureRep
    TextLink = TextLinkRep
    def __init__(self, rep=None, name=None):
        self.name = name
        super().__init__(rep)

    def __eq__(self, otherUser):
        # TODO: extract ids and make this better
        return self.name == otherUser.name

    def __lt__(self, otherUser):
        return self.name < otherUser.name

    def __le__(self, otherUser):
        return self.__lt__(otherUser) or self.__eq__(otherUser)

    def __gt__(self, otherUser):
        return not self.__lt__(otherUser)

    def __ge__(self, otherUser):
        return self.__gt__(otherUser) or self.__eq__(otherUser)