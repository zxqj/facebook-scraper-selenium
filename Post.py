from RepresentedObject import RepresentedObject
from Representation import Representation
from User import User
def strip(string):
    """Helping function to remove all non alphanumeric characters"""
    words = string.split()
    words = [word for word in words if "#" not in word]
    string = " ".join(words)
    clean = ""
    for c in string:
        if str.isalnum(c) or (c in [" ", ".", ","]):
            clean += c
    return clean

class InFeedRepresentation(Representation):

    def __init__(self, rootNode):
        super().__init__(rootNode)

    def createObject(self, dataObject=None):
        if (dataObject is None):
            dataObject = RepresentedObject()
        userRep = User.CirclePicture.get(self.node)
        dataObject.user = User(userRep)
        # Creating a time entry.
        time_element = self.node.find_element_by_css_selector("abbr")
        dataObject.time = time_element.get_attribute("data-utime")
        # Creating post text entry
        dataObject.content = self.node.find_element_by_class_name("userContent").text
        dataObject.status = strip(dataObject.content)

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, InFeedRepresentation)

    @staticmethod
    def getAll(rootNode):
        return [InFeedRepresentation(node) for node in rootNode.find_elements_by_class_name("userContentWrapper")]

class Post(RepresentedObject):
    InFeed = InFeedRepresentation
    def __init__(self, rep):
        super().__init__(rep)