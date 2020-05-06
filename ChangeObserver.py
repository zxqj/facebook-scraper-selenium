import Json
from Poll import Poll
from User import User
from functools import reduce
from Post import PollPost
import time

class ChangeObserver(object):
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.newState = self.lastState = None

    def generateNextState(self):
        pass

    def describeChange(self, x1, x2):
        pass

    def run(self):
        while (True):
            if (self.lastState is None):
                self.newState = self.lastState = self.generateNextState()
                time.sleep(self.delay)
                continue
            self.lastState = self.newState
            self.newState = self.generateNextState()
            if not (self.newState == self.lastState):
                self.callback(self.describeChange(self.lastState, self.newState))
            time.sleep(self.delay)

class PollPostChangeObserver(ChangeObserver):
    def __init__(self, delay, callback, reader, pollPostUrl):
        super().__init__(delay, callback)
        self.reader = reader
        self.pollPostUrl = pollPostUrl

    def generateNextState(self):
        postRep = self.reader.readPostAs(PollPost.PostInFeed, url=self.pollPostUrl)
        poll = PollPost(postRep).poll
        print(Json.encode(poll))
        return poll

    def describeChange(self, poll1, poll2):
        changes = []
        def added(user, option):
            changes.append({"type": "+", "user": user, "option": option})
        def removed(user, option):
            changes.append({"type": "-", "user": user, "option": option})

        curPollOptions = frozenset(poll1.votes.keys())
        nextPollOptions = frozenset(poll2.votes.keys())

        for removedOption in curPollOptions.difference(nextPollOptions):
            for user in poll1.votes.get(removedOption):
                removed(user,removedOption)

        for addedOption in nextPollOptions.difference(curPollOptions):
            for user in poll2.votes.get(addedOption):
                added(user,addedOption)

        for option in curPollOptions.intersection(nextPollOptions):
            lastStateUsers = poll1.votes.get(option)
            nextStateUsers = poll2.votes.get(option)

            lastStateUsers.sort()
            nextStateUsers.sort()
            i = j = 0
            while i < len(lastStateUsers) and j < len(nextStateUsers):
                curLastStateUser = lastStateUsers[i]
                curNextStateUser = nextStateUsers[j]
                if (curLastStateUser == curNextStateUser):
                    i = i + 1
                    j = j + 1
                elif curNextStateUser > curLastStateUser:
                    # ["a","b"]
                    # ["a","c"]
                    changes.append({"type": "-", "user": curLastStateUser, "option": option})
                    i = i + 1
                else:
                    # ["a", "c"]
                    # ["a", "b"]
                    changes.append({"type": "+", "user": curNextStateUser, "option": option})
                    j = i + 1

            if j < len(nextStateUsers):
                changes.extend([{"type": "+", "user": user, "option": option} for user in nextStateUsers[j:]])

            if i < len(lastStateUsers):
                changes.extend([{"type": "-", "user": user, "option": option} for user in lastStateUsers[i:]])

        changes.sort(key=lambda change: change["user"])
        mapObj = map(lambda change: '{user.name} {action} {option}'.format(user=change['user'], action=('voted for' if change.get("type") == '+' else 'removed vote from'), option=change['option']), changes)
        return [x for x in mapObj]

if __name__ == "__main__":

    def getPollObj(d):
        votes=dict()
        for k,v in d.items():
            votes[k] = [User(name=n) for n in v]
        return Poll(votes=votes)

    def runTest(votes1, votes2, expectedResults):
        ppco = PollPostChangeObserver(None,None,None,None)
        curState = getPollObj(votes1)
        nextState = getPollObj(votes2)
        result = [x for x in ppco.describeChange(curState, nextState)]
        passed = reduce(lambda x,y: x and (y in result), expectedResults, True) and len(expectedResults) == len(result)
        print("Passed" if passed else "Failed")

    runTest({"Michelle": ["Patrick"], "Richard": []},
            {"Michelle": ["Patrick"], "Richard": ["Patrick"]},
            ["Patrick voted for Richard"])
    runTest({"Michelle": ["Patrick"], "Richard": []},
            {"Michelle": [], "Richard": ["Patrick"]},
            ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    runTest({"Michelle": ["Patrick"]},
            {"Richard": ["Patrick"]},
            ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    runTest({ "Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim"],
              "Michelle": ["Richard", "Steven", "Molly", "Jennifer", "Renee", "Dianne"],
              "Joe": ["Patrick"] },
            { "Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim", "Steven"],
              "Michelle": ["Richard", "Molly", "Jennifer", "Renee", "Dianne", "Patrick"] },
            ["Patrick voted for Michelle", "Patrick removed vote from Joe", "Steven voted for Renee", "Steven removed vote from Michelle"])
