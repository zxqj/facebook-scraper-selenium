from models.RepresentedObject import RepresentedObject
from models.Representation import Representation
from models.Poll import Poll
from models.User import User
from Json import encode

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

    def create_object(self, dataObject=None):
        if (dataObject is None):
            dataObject = RepresentedObject()
        userRep = User.CirclePicture.get(self.node)
        dataObject.user = User(userRep)
        # Creating a time entry.
        time_element = self.node.find_element_by_css_selector("abbr")
        dataObject.time = time_element.get_attribute("data-utime")
        # Creating post text entry
        dataObject.content = self.node.find_element_by_class_name("userContent").text

    def is_poll(self):
        return len(Poll.InPost.get_all(self.node)) > 0

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, InFeedRepresentation)

    @staticmethod
    def get_all(rootNode):
        return [InFeedRepresentation(node) for node in rootNode.find_elements_by_class_name("userContentWrapper")]


class PollPostRepresentation(InFeedRepresentation):
    def __init__(self, node):
        super().__init__(node)

    def create_object(self, dataObject=None):
        super().create_object(dataObject)
        pollRep = Poll.InPost.get(self.node.parent)
        dataObject.poll = Poll(rep=pollRep)

    def is_open(self):
        return len(self.node.find_elements_by_xpath("//span[contains(text(), 'turned off commenting for this post')]")) > 0

    @staticmethod
    def get(rootNode):
        return Representation.get(rootNode, PollPostRepresentation)

    @staticmethod
    def get_all(rootNode):
        results = rootNode.find_elements_by_class_name("userContentWrapper")
        return [PollPostRepresentation(node) for node in results]

class Post(RepresentedObject):
    InFeed = InFeedRepresentation
    def __init__(self, rep=None, user=None, time=None, content=None):
        self.user = user
        self.time = time
        self.content = content
        super().__init__(rep)

    def __eq__(self, otherPost):
        return self.user == otherPost.user and self.time == otherPost.time and self.content == otherPost.content

class PollPost(Post):
    PostInFeed = PollPostRepresentation
    def __init__(self, rep=None, user=None, time=None, content=None, poll=None):
        self.poll = poll
        super().__init__(rep=rep, user=user, time=time, content=content)

    def __eq__(self, otherPost):
        return super() == otherPost and self.poll == otherPost.poll


if __name__ == "__main__":
    user = User(name="Michelle Saavedra")
    posterUser = User(name="Garrett Baca")
    poll = Poll(votes=dict({"Patrick": ["Michelle", "Richard"]}), poster=posterUser)
    pollPost = PollPost(user=user, time=333352352, content="Some facebook post content", poll=poll)
    print(encode(pollPost))