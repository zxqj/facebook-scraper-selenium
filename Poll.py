import Browser
from Representation import Representation
from RepresentedObject import RepresentedObject
from functools import reduce
from User import User
import time

class InPostRepresentation(Representation):
    def __init__(self, node):
        super().__init__(node)

    def createObject(self, dataObject):
        dataObject.votes = dict()
        pollOptionSplitters = self.node.find_elements_by_xpath(".//div[text()='Voters for this option']")
        for pollOptionSplitter in pollOptionSplitters:
            optionParent = pollOptionSplitter.find_elements_by_xpath("./preceding-sibling::div")[0]
            optionInput = optionParent.find_elements_by_tag_name('input')[0]
            optionInputValue = optionInput.get_attribute('aria-label')
            valuesParent = pollOptionSplitter.find_elements_by_xpath("./following-sibling::div")[0]
            users = [User(rep) for rep in User.CirclePicture.getAll(valuesParent)]
            moreVotersDialogButton = valuesParent.find_elements_by_xpath('.//a[contains(@href,"browse/option_voters")]')
            if (not (moreVotersDialogButton == None)) and len(moreVotersDialogButton) > 0:
                moreVotersDialogButton = moreVotersDialogButton[0]
                # we must scroll once after we exit the dialog box, this might need to be made more robust
                Browser.get().execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                moreVotersDialogButton.click()
                time.sleep(10)
                xpathexpr = '//div[contains(@class,"profileBrowserDialog")]'
                dialogNode = self.node.find_elements_by_xpath(xpathexpr)[0]
                users = [User(rep=rep) for rep in User.CirclePicture.getAll(dialogNode)]
                dialogNode.find_elements_by_xpath('.//a[contains(@data-testid, "dialog_title_close_button")]')[0].click()
                time.sleep(10)

            dataObject.votes[optionInputValue] = users

    @staticmethod
    def get(rootNode):
        nodes = InPostRepresentation.getAll(rootNode)
        return None if len(nodes) == 0 else nodes[0]

    @staticmethod
    def getAll(rootNode):
        return [InPostRepresentation(node) for node in rootNode.find_elements_by_class_name("mtm")]

class Poll(RepresentedObject):
    InPost = InPostRepresentation
    def __init__(self, rep=None, votes=dict()):
        self.votes = votes
        super().__init__(rep)

    def __eq__(self, otherPoll):
        votesTheSame = True
        # make sure that for all options in our votes, the voters for that option are the same in both polls
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
            votesTheSame = reduce(lambda truthVal, nextIndex: truthVal and users[nextIndex] == otherUsers[nextIndex], range(len(users)), votesTheSame)

        # make sure that no options exist in other poll which exit in ours
        return votesTheSame and len(frozenset(otherPoll.votes.keys()).difference(frozenset(self.votes.keys()))) == 0


if __name__ == "__main__":
    def runTest(votes1, votes2, truthVal):
        poll1 = Poll(votes=votes1)
        poll2 = Poll(votes=votes2)
        assert truthVal is (poll1 == poll2)

    runTest({"Michelle": ["Patrick"], "Richard": []},
            {"Michelle": ["Patrick"], "Richard": ["Patrick"]}, False)
    runTest({"Michelle": ["Patrick"], "Richard": ["Patrick"]},
            {"Michelle": ["Patrick"], "Richard": ["Patrick"]}, True)
    runTest({"Michelle": ["Patrick"], "Richard": []},
            {"Michelle": [], "Richard": ["Patrick"]}, False)
    runTest({"Michelle": ["Patrick"]},
            {"Richard": ["Patrick"]}, False)
    runTest({ "Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim"],
              "Michelle": ["Richard", "Steven", "Molly", "Jennifer", "Renee", "Dianne"],
              "Joe": ["Patrick"] },
            { "Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim", "Steven"],
              "Michelle": ["Richard", "Molly", "Jennifer", "Renee", "Dianne", "Patrick"] }, False)