from functools import reduce

from ChangeObserver import ChangeObserver
from models.Poll import Poll
from models.Post import PollPost
from models.User import User, get_poll_option
from output import debug, notify
from datetime import datetime
import dateparser

def format_poll_option(option, voters):
    voterString = reduce(lambda x,y: x+", "+y, map(lambda u: u.name, voters))
    return '{o}: {v}'.format(o=option, v=voterString)

class PollPostChangeObserver(ChangeObserver):
    def __init__(self, delay, callback, reader, url, player_list = [], deadline = None,
                 complete_on_quorum = False,
                 notify_on_complete = False):
        super().__init__(delay, callback)
        self.reader = reader
        self.url = url
        self.player_list = player_list
        self.complete_on_quorum = complete_on_quorum
        self.notify_on_complete = notify_on_complete
        self.deadline = deadline

    @staticmethod
    def are_all_votes_in(votes, player_list):
        player_list_set = set(player_list)
        players_as_options_set = set([get_poll_option(name) for name in player_list])
        # we're going to see if the set of all voters for valid options subsumes the player list
        votes_in = reduce(lambda a, b: a.union(b), [set([voter.name for voter in voters]) for option, voters in votes.items() if option in players_as_options_set])
        return votes_in.issuperset(player_list_set)

    def check_finished(self, votes):
        if not ((self.complete_on_quorum and len(self.player_list) > 0) or not (self.deadline is None)):
            return False
        elif not (self.deadline is None) and self.deadline < datetime.now():
            return True
        else:
            return PollPostChangeObserver.are_all_votes_in(votes, self.player_list)

    def generate_next_state(self):
        postRep = self.reader.read_post_as(PollPost.PostInFeed, url=self.url)
        poll = PollPost(postRep).poll
        finished = self.check_finished(poll.votes)
        if finished and self.notify_on_complete:
            notify("All votes are in.")
        debug(*[format_poll_option(option, voters) for option, voters in poll.votes.items()])
        return poll, finished

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
    print(("Passed" if passed else "Failed")+" vote changes tests")

def run_completed_test(player_list, deadline, votes, expectedFinished):
    def dummy_callback(blah):
        pass
    player_list = ["A", "B", "C"]
    deadline = None
    # simple completed
    votes = {"A": ["B", "C"], "B": ["A"]}
    ppco = PollPostChangeObserver(0, dummy_callback, None, None,
                                  player_list = player_list, deadline=deadline, complete_on_quorum=True)
    passed = ppco.check_finished(votes) == expectedFinished
    print(("Passed" if passed == expectedFinished else "Failed") + " vote-completed tests")

if __name__ == "__main__":
    # vote added
    run_test({"Michelle": ["Patrick"], "Richard": []},
             {"Michelle": ["Patrick"], "Richard": ["Patrick"]},
             ["Patrick voted for Richard"])
    # vote removed
    run_test({"Michelle": ["Patrick"], "Richard": []},
             {"Michelle": [], "Richard": ["Patrick"]},
             ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    # vote changed
    run_test({"Michelle": ["Patrick"]},
             {"Richard": ["Patrick"]},
             ["Patrick voted for Richard", "Patrick removed vote from Michelle"])
    run_test({"Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim"],
              "Michelle": ["Richard", "Steven", "Molly", "Jennifer", "Renee", "Dianne"],
              "Joe": ["Patrick"]},
             {"Renee": ["Maria", "Chuck", "Joe", "Keri", "Angela", "Christopher", "Jim", "Steven"],
              "Michelle": ["Richard", "Molly", "Jennifer", "Renee", "Dianne", "Patrick"]},
             ["Patrick voted for Michelle", "Patrick removed vote from Joe", "Steven voted for Renee",
              "Steven removed vote from Michelle"])
    player_list = ["Joe", "Jim", "Patrick"]
    complete_vote = {"Patrick": ["Jim", "Joe"], "Joe": ["Patrick"]}
    incomplete_vote = {"Patrick": ["Jim", "Joe"]}

    # everyone has voted, no invalid options, no invalid voters
    run_completed_test(player_list, None, complete_vote, True)
    # not everyone has voted, no invalid options, no invalid voters
    run_completed_test(player_list, None, incomplete_vote, False)
    # not everyone has voted but deadline passed, no invalid options, no invalid voters
    run_completed_test(player_list, dateparser.parse("a minute ago"), incomplete_vote, True)
    # everyone has voted, one invalid option, no invalid voters
    patrick_cant_even = dict(incomplete_vote)
    patrick_cant_even["I can't even"] = ["Patrick"]
    run_completed_test(player_list, None, patrick_cant_even, False)
    # everyone has voted, no invalid options, one invalid voter
    # mehh, this will work
