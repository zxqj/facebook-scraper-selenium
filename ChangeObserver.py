from models.Poll import Poll
from models.User import User
from functools import reduce
from models.Post import PollPost
import time
from output import debug

class ChangeObserver(object):
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.newState = self.lastState = None

    def generate_next_state(self):
        pass

    def describe_change(self, x1, x2):
        pass

    def generate_and_time_next_state(self):
        start = time.time()
        res = self.generate_next_state()
        debug("check completed ("+str(int(time.time() - start)) + "s)")
        return res

    def run(self):
        while (True):
            if (self.lastState is None):
                res = self.generate_and_time_next_state()
                self.newState = self.lastState = res
                time.sleep(self.delay)
                continue
            self.lastState = self.newState
            self.newState = self.generate_and_time_next_state()
            if not (self.newState == self.lastState):
                self.callback(self.describe_change(self.lastState, self.newState))
            time.sleep(self.delay)

def format_poll_option(option, voters):
    voterString = reduce(lambda x,y: x+", "+y, map(lambda u: u.name, voters))
    return '{o}: {v}'.format(o=option, v=voterString)

class PollPostChangeObserver(ChangeObserver):
    def __init__(self, delay, callback, reader, pollPostUrl):
        super().__init__(delay, callback)
        self.reader = reader
        self.pollPostUrl = pollPostUrl

    def generate_next_state(self):
        postRep = self.reader.read_post_as(PollPost.PostInFeed, url=self.pollPostUrl)
        poll = PollPost(postRep).poll
        debug(*[format_poll_option(option, voters) for option, voters in poll.votes.items()])
        return poll

    def describe_change(self, poll1, poll2):
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

    def get_poll_obj(d):
        votes=dict()
        for k,v in d.items():
            votes[k] = [User(name=n) for n in v]
        return Poll(votes=votes)

    def run_test(votes1, votes2, expectedResults):
        ppco = PollPostChangeObserver(None,None,None,None)
        curState = get_poll_obj(votes1)
        nextState = get_poll_obj(votes2)
        result = [x for x in ppco.describe_change(curState, nextState)]
        passed = reduce(lambda x,y: x and (y in result), expectedResults, True) and len(expectedResults) == len(result)
        print("Passed" if passed else "Failed")

    run_test({"Michelle": ["Patrick"], "Richard": []},
             {"Michelle": ["Patrick"], "Richard": ["Patrick"]},
             ["Patrick voted for Richard"])
    run_test({"Michelle": ["Patrick"], "Richard": []},
             {"Michelle": [], "Richard": ["Patrick"]},
             ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    run_test({"Michelle": ["Patrick"]},
             {"Richard": ["Patrick"]},
             ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    run_test({"Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim"],
              "Michelle": ["Richard", "Steven", "Molly", "Jennifer", "Renee", "Dianne"],
              "Joe": ["Patrick"]},
             { "Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim", "Steven"],
              "Michelle": ["Richard", "Molly", "Jennifer", "Renee", "Dianne", "Patrick"] },
             ["Patrick voted for Michelle", "Patrick removed vote from Joe", "Steven voted for Renee", "Steven removed vote from Michelle"])
