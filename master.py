import itertools
from scipy.stats import entropy
import pdb
import copy
import argparse


def perm_with_replace(elements, slots):
    results = []
    for c in itertools.product(elements, repeat=slots):
        results.append(c)
    return results


class CodeBreaker:

    def __init__(self, replace=False):

        #COLORS = ["black", "blue", "brown", "green", "orange", "red", "white", "yellow"]
        #COLORS = ["orange", "brown", "pink", "purple", "red", "blue"]
        COLORS = ["brown", "pink", "purple", "red", "blue", "greeb"]

        self.full_space = []
        self.observations = []

        if not replace:
            for sequence in itertools.permutations(COLORS, 4):
                self.full_space.append(Scenario(sequence))
        else:
            for sequence in perm_with_replace(COLORS, 4):
                self.full_space.append(Scenario(sequence))

        self.experiment_space = perm_with_replace(COLORS, 4)

        self.feasible_space = copy.deepcopy(self.full_space)

        print(f"{len(self.full_space)} sequences are possible")

    def add_observation(self, trial):
        self.observations.append(trial)

    def propose_sequence(self):

        maxent = 0
        best = None

        for hypo in self.experiment_space:
            cdist = {}
            for scenario in self.feasible_space:
                prediction = scenario.predict(hypo)
                pkey = "-".join(prediction)
                if pkey not in cdist:
                    cdist[pkey] = 0
                cdist[pkey] += 1
            cent = self.get_entropy(cdist)
            if cent > maxent:
                maxent = cent
                best = hypo

        return best

    def get_entropy(self, dist):
        full = [0] * 12
        flat = [count for _, count in dist.items()]
        full[0:len(flat)+1] = flat
        return entropy(full)


    def try_reduction(self, observations):

        feasible_space = []

        for s in self.feasible_space:
            if s.is_compatible(observations):
                feasible_space.append(s)

        reduction = len(self.feasible_space) - len(feasible_space)

        return feasible_space, reduction

    def commit_reduction(self):

        self.feasible_space, reduction = self.try_reduction(self.observations)
        print(f"Feasible space reduced by {reduction}")
        print(f"{len(self.feasible_space)} sequences are now possible")
        if len(self.feasible_space) <= 8:
            print("They are:")
            for s in self.feasible_space:
                print(s.sequence)

    def cracked(self):
        if len(self.feasible_space) == 1:
            print("Code cracked!")
            return True

        if len(self.feasible_space) == 0:
            raise BaseException("Fatal error -- no sequences possible")

        return False


class Scenario():

    def __init__(self, sequence):
        self.sequence = sequence

    def is_compatible(self, observations):
        for observation in observations:
            prediction = self.predict(observation.input)
            if prediction  != observation.output:
                return False

        return True

    def predict(self, probe):
        result = []
        wrongpos = []
        remainder = list(probe)
        for i, e in enumerate(self.sequence):
            if e == probe[i]:
                result.append('1')
                remainder.remove(e)
            else:
                wrongpos.append(e)

        for w in wrongpos:
            if w in remainder:
                result.append('0')
                remainder.remove(w)

        return sorted(result, reverse=True)


class Experiment():

    def __init__(self, sequence):
        self.input = sequence
        self.output = None

    def update_result(self, result):
        self.output = (result)

if __name__ == "main":







    cb = CodeBreaker(False)
    i = 0

    while not cb.cracked():

        if i == 0:
            #tseq = ["black", "blue", "brown", "green"]
            tseq = ["orange", "brown", "pink", "purple"]
        else:
            tseq = cb.propose_sequence()

        print("Try the sequence:")
        print(tseq)
        result = input("Enter result >> ").replace(" ", "").split(",")
        if result == ['']:
            result = []

        cx = Experiment(tseq)
        cx.update_result(result)
        cb.add_observation(cx)
        cb.commit_reduction()
        i += 1
