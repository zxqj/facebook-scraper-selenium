from Representation import Representation
from RepresentedObject import RepresentedObject
from functools import reduce
from User import User

class InPostRepresentation(Representation):
    def __init__(self, node):
        super().__init__(node)

    def createObject(self, dataObject):
        userRep = User.CirclePicture.get(self.node)
        pollOptionSplitters = self.node.find_elements_by_xpath(".//div[text()='Voters for this option']")
        for pollOptionSplitter in pollOptionSplitters:
            optionParent = pollOptionSplitter.find_elements_by_xpath("./preceding-sibling::div")[0]
            optionInput = optionParent.find_elements_by_tag_name('input')[0]
            optionInputValue = optionInput.get_attribute('aria-label')
            valuesParent = pollOptionSplitter.find_elements_by_xpath("./following-sibling::div")[0]
            valueReps = User.SmallCirclePicture.getAll(valuesParent)
            dataObject.votes[optionInputValue] = [User(rep) for rep in valueReps]

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, InPostRepresentation)

    @staticmethod
    def getAll(rootNode):
        return [InPostRepresentation(node) for node in rootNode.find_elements_by_class_name("mtm")]

class Poll(RepresentedObject):
    InPost = InPostRepresentation
    def __init__(self, rep=None, votes=dict()):
        self.votes = votes
        super().__init__(rep)

    def didChange(self, otherPoll):
        votesTheSame = True
        for option, users in self.votes.items():
            otherUsers = otherPoll.votes.get(option)
            if (otherUsers is None):
                votesTheSame = False
                break
            if not (len(otherUsers) is len(users)):
                votesTheSame = False
                break
            users.sort()
            otherUsers.sort()
            votesTheSame = reduce(lambda truthVal, nextIndex: truthVal and not users[nextIndex].didChange(otherUsers[nextIndex]), range(len(users)), votesTheSame)

        return not (self.poster is otherPoll.poster and votesTheSame)