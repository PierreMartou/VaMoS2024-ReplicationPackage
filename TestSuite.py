import os
import pickle
import time
from random import randrange
from CITSAT import CITSAT
from RandomSampling import randomSampling, computeCoverage, invalidChance
from ResultRefining import printCoveringArray, numberOfChangements
from SystemData import SystemData
from SATSolver import SATSolver
from CTT_heuristics import BuildingCTT


def computeCITSuite(fpath, iteration, s, candidates=30, recompute=False):
    filepath = fpath + str(iteration)+".pkl"
    if os.path.exists(filepath) and not recompute:
        testSuite = readSuite(filepath)
    else:
        testSuite = TestSuite(s, CITSAT(s, False, candidates), computeRearrangements=True)
        storeSuite(testSuite, filepath)
    return testSuite


def computeCTTSuite(fpath, iteration, s, candidates=30, interaction_filter=False, weight_lookahead=0, weight_comparative=0, recompute=False):
    filepath = fpath + str(iteration)+".pkl"
    if os.path.exists(filepath) and not recompute:
        testSuite = readSuite(filepath)
    else:
        t = BuildingCTT(s, verbose=False, numCandidates=candidates, interaction_filter=interaction_filter, weight_lookahead=weight_lookahead, weight_comparative=weight_comparative)
        testSuite = TestSuite(s, t.getCoveringArray())
        storeSuite(testSuite, filepath)
    return testSuite


def readSuite(filePath):
    suite = pickle.load(open(filePath, 'rb'))
    return suite


def storeSuite(suite, filePath):
    f = open(filePath, "wb")
    pickle.dump(suite, f)
    f.close()

class TestSuite:
    def __init__(self, systemData, suite, computeRearrangements=False):
        if len(suite) == 0:
            print("WARNING: Creating a Test Suite with no elements.")
        self.suiteUnordered = suite
        self.computeRearrangements = computeRearrangements
        self.systemData = systemData
        self.contexts = systemData.getContexts()
        self.features = systemData.getFeatures()
        self.coreContexts = systemData.getContexts()
        self.coreFeatures = systemData.getFeatures()
        for testCase in suite:
            for c in self.coreContexts:
                if testCase[c] < 0:
                    self.coreContexts.remove(c)
            for f in self.coreFeatures:
                if testCase[f] < 0:
                    self.coreFeatures.remove(f)

        self.variabilities = self.features.copy()
        for f in self.coreFeatures:
            self.variabilities.remove(f)

        if computeRearrangements:
            if len(systemData.getContexts()) != 0:
                self.suiteMinimized = self.minimizeTestEffort(suite, systemData.getContexts())
            else:
                self.suiteMinimized = self.minimizeTestEffort(suite, systemData.getFeatures())
            self.suiteMaximized = self.maximizeDissimilarity(suite, systemData.getFeatures())
            self.suiteRandomOrder = self.randomOrder()

    def compareFeatureSwitches(self):
        minimizedFeatureSwitches = numberOfChangements(self.suiteMinimized, self.features)
        maxFeatureSwitches = numberOfChangements(self.suiteMaximized, self.features)
        print("Minimized feature switches : " + str(minimizedFeatureSwitches))
        print("Maximized feature switches : " + str(maxFeatureSwitches))

    def findConfiguration(self, initNumber):
        if initNumber < 0 or initNumber >= len(self.suiteMinimized):
            print("n is larger than the length of the test suite or smaller than 0. Can't find configuration.")
            return None

        config = self.suiteMinimized[initNumber]

        correspondingNumber = 0
        for test in self.suiteMaximized:
            if config == test:
                break
            else:
                correspondingNumber += 1

        if self.suiteMinimized[initNumber] != self.suiteMaximized[correspondingNumber]:
            print("ERROR AT FINDING SIMILAR CONFIGURATIONS.")

        print("Activation order of test " + str(initNumber) + ", ordered test suite: ")
        # print(self.suite[initNumber])
        print(self.activationOrder(initNumber, self.suiteMinimized))
        print("Activation order of test " + str(correspondingNumber) + ", unordered test suite: ")
        # print(self.suite[correspondingNumber])
        print(self.activationOrder(correspondingNumber, self.suiteMaximized))

    def interactionTransitionCoverageEvolution(self):
        valuesForFactors = self.systemData.getValuesForFactors()
        solver = SATSolver(self.systemData)
        unCovInteractions = []
        unCovTransitions = []
        factors = list(valuesForFactors.keys())
        for i in range(len(factors) - 1):
            for j in range(len(valuesForFactors[factors[i]])):
                pair1 = (factors[i], valuesForFactors[factors[i]][j])
                for i2 in range(i + 1, len(factors)):
                    for j2 in range(len(valuesForFactors[factors[i2]])):
                        pair2 = (factors[i2], valuesForFactors[factors[i2]][j2])

                        if solver.checkSAT([pair1[1], pair2[1]]):
                            # Each set is a [Factor, Value, Factor, Value, ...] tuple
                            unCovInteractions.append([pair1, pair2])
                            if solver.checkSAT([-1*pair1[1], -1*pair2[1]]):
                                unCovTransitions.append([pair1, pair2])

        maxInteractions = len(unCovInteractions)
        maxTransitions = len(unCovTransitions)
        interactionEvolution = []
        transitionEvolution = []
        switchesEvolution = []
        suite = self.getUnorderedTestSuite()
        factors = list(valuesForFactors.keys())
        prevTestCase = None
        for testCase in suite:
            interactions = []
            for i in range(len(factors)-1):
                pair1 = (factors[i], testCase[factors[i]])
                for j in range(i+1, len(factors)):
                    pair2 = (factors[j], testCase[factors[j]])
                    interactions.append([pair1, pair2])
            transitions = []
            if prevTestCase is not None:
                transitions = [pair for pair in interactions if prevTestCase[pair[0][0]] != pair[0][1] and prevTestCase[pair[1][0]] != pair[1][1]]
                switchesEvolution.append(sum([1 for f in factors if prevTestCase[f] != testCase[f]]))
            prevTestCase = testCase

            for interaction in interactions:
                if interaction in unCovInteractions:
                    unCovInteractions.remove(interaction)
            interactionEvolution.append(100.0-100.0*len(unCovInteractions)/maxInteractions)
            for transition in transitions:
                if transition in unCovTransitions:
                    unCovTransitions.remove(transition)
            transitionEvolution.append(100.0-100.0*len(unCovTransitions)/maxTransitions)
        if len(unCovInteractions) != 0 or len(unCovTransitions) != 0:
            print("WARNING : IN COMPUTING COVERAGE EVOLUTION, COVERAGE DID NOT REACH 100%.")
        return interactionEvolution, transitionEvolution, switchesEvolution

    # Computes all transitions covered in this test suite, with the order being specified.
    def transitionPairCoverage(self, mode):
        if len(self.suiteMinimized) < 2:
            print("There are no transitions in a test suite with only one configuration.")
            return []

        if mode == None:
            print("Please provide a mode when computing transition pairs coverage.")

        transitions = []
        suite = self.suiteRandomOrder
        if mode == "minimized":
            suite = self.suiteMinimized
        elif mode == "unordered":
            suite = self.suiteUnordered
        elif mode == "random":
            suite = self.suiteRandomOrder
        elif mode == "dissimilarity":
            suite = self.suiteMaximized
        else:
            print("The mode was not recognized.")

        prev = suite[0]
        for test in suite[1:]:
            changes = []
            for f in self.variabilities:
                if prev[f] != test[f]:
                    sign = "+" if test[f] > 0 else "-"
                    changes.append(sign + f)
            for i in range(len(changes)):
                for j in range(i+1, len(changes)):
                    pair = (changes[i], changes[j])
                    mirrorPair = (changes[j], changes[i])
                    if pair not in transitions and mirrorPair not in transitions:
                        transitions.append(pair)
            prev = test
        return transitions

    def activationCoverage(self, suite):
        featurePairs = dict.fromkeys([f for f in self.features if f not in self.coreFeatures])
        for f in featurePairs:
            featurePairs[f] = set()
        for nTest in range(len(suite)):
            activationOrder = [f for f in self.activationOrder(nTest, suite) if "Test number " not in f]
            for fTest in range(len(activationOrder)-1):
                currFeature = activationOrder[fTest]
                for fprimeTest in range(fTest+1, len(activationOrder)):
                    featurePairs[currFeature].add(activationOrder[fprimeTest])
        return sum([len(featurePairs[f]) for f in featurePairs])

    def analyseActivationCoverage(self, verbose=False):
        orderedScore = self.activationCoverage(self.suiteMinimized)
        if verbose:
            print("Number of feature pairs for ordered test suite: " + str(orderedScore))

        unorderedScore = self.activationCoverage(self.suiteMaximized)
        if verbose:
            print("Number of feature pairs for unordered test suite: " + str(unorderedScore))
        # print((0.0+unorderedScore-orderedScore)/unorderedScore)
        return unorderedScore, orderedScore, (0.0+unorderedScore-orderedScore)/unorderedScore

    def activationOrder(self, n, suite):
        if n < 0 or n >= len(suite):
            print("n is larger than the length of the test suite or smaller than 0.")
            return None

        activationOrder = []
        nTest = 0
        for test in suite[:n+1]:
            activationOrder = activationOrder + ["Test number "+str(nTest)]
            nTest += 1
            # Removing features deactivated
            for feature in self.variabilities:
                if test[feature] < 0 and feature in activationOrder:
                    activationOrder.remove(feature)
            for feature in self.variabilities:
                if test[feature] > 0 and feature not in activationOrder:
                    activationOrder.append(feature)
        finalOrder = []
        for x in range(len(activationOrder)-1):
            if "Test number " in activationOrder[x] and "Test number " in activationOrder[x+1]:
                pass
            else:
                finalOrder.append(activationOrder[x])
        finalOrder.append(activationOrder[len(activationOrder)-1])
        return finalOrder

    def computeDistribution(self, n, suite):
        activationOrder = self.activationOrder(n, suite)
        totalFeatures = len([f for f in activationOrder if "Test number " not in f])
        numberOfTests = len([f for f in activationOrder if "Test number " in f])
        return totalFeatures, numberOfTests, float(totalFeatures)/numberOfTests, (numberOfTests+0.0)/totalFeatures

    # computes test score with different weights on the features
    def testWeightScore(self, activationOrder):
        maxScore = 0
        score = 0
        snapshot = 0
        for feature in range(len(activationOrder)-1):
            if "Test number " in activationOrder[feature]:
                maxScore += score
                snapshot = score
            else:
                score += 1
        if snapshot == 0:
            return 0
        return maxScore/snapshot

    def compareDistribution(self, verbose=False):
        init = 5
        end = len(self.suiteMaximized)
        numberOfOrders = end - init
        unorderedTotalFeatures = 0.0
        unorderedNumberOfTests = 0.0
        unorderedAverage = 0.0
        unorderedScore = 0.0

        for i in range(init, end):
            r = self.computeDistribution(i, self.suiteMaximized)
            unorderedTotalFeatures += r[0]
            unorderedNumberOfTests += r[1]
            unorderedAverage += r[2]
            unorderedScore += r[3]
            # print(self.activationOrder(i))
        if verbose:
            print("Unordered suite distribution, average on all tests:")
            print("Number of features: " + str(unorderedTotalFeatures/numberOfOrders)
                  + "; number of tests: " + str(unorderedNumberOfTests/numberOfOrders)
                  + "; average: " + str(unorderedAverage/numberOfOrders)
                  + "; test score: " + str(unorderedScore/numberOfOrders))
        unOrderedResult = [unorderedTotalFeatures/numberOfOrders, unorderedNumberOfTests/numberOfOrders,
                           unorderedAverage/numberOfOrders, unorderedScore/numberOfOrders]

        minimizedTotalFeatures = 0.0
        minimizedNumberOfTests = 0.0
        minimizedAverage = 0.0
        minimizedScore = 0.0
        for i in range(init, end):
            r = self.computeDistribution(i, self.suiteMinimized)
            minimizedTotalFeatures += r[0]
            minimizedNumberOfTests += r[1]
            minimizedAverage += r[2]
            minimizedScore += r[3]
            # print(self.activationOrder(i))
        if verbose:
            print("Minimized suite distribution, average on all tests:")
            print("Number of features: " + str(minimizedTotalFeatures/numberOfOrders) + "; number of tests: " + str(minimizedNumberOfTests/numberOfOrders) + "; average: " + str(minimizedAverage/numberOfOrders))

        minimizedResult = [minimizedTotalFeatures/numberOfOrders, minimizedNumberOfTests/numberOfOrders,
                           minimizedAverage/numberOfOrders, minimizedScore/numberOfOrders]

        return unOrderedResult + minimizedResult

    def randomOrder(self):
        suite = self.suiteUnordered.copy()
        randomlyOrderedSuite = []
        while suite:
            index = randrange(len(suite))
            randomlyOrderedSuite.append(suite[index])
            suite.remove(suite[index])
        return randomlyOrderedSuite


    """ Sorts the array to minimize the testing effort needed to simulate it.
    """
    def minimizeTestEffort(self, givenArray, nodes, nPrevTests=0):
        array = givenArray.copy()
        newArray = []
        prevTest = []
        if nPrevTests > 0:
            for i in range(nPrevTests):
                prevTest = array[0]
                newArray.append(prevTest)
                array.remove(prevTest)
        else:
            prevTest = min(array, key=lambda testCase: sum([1 for c in nodes if testCase[c] > 0]))
            newArray = [prevTest]
            array.remove(prevTest)

        collision = 0
        while array:  # until all test cases are transferred
            minScore = self.effortDistance(array[0], prevTest, nodes)
            bestTestCase = array[0]
            for testCase in array:
                currentScore = self.effortDistance(testCase, prevTest, nodes)
                if currentScore == minScore:
                    collision += 1
                if currentScore < minScore:
                    minScore = currentScore
                    bestTestCase = testCase

            prevTest = bestTestCase
            newArray.append(prevTest)
            array.remove(prevTest)
        # print("The number of collisions encountered while sorting is: " + str(collision))
        return newArray

    """Returns the distance between t1 and t2, only for features/contexts contained in nodes.
    """
    def effortDistance(self, t1, t2, nodes=None):
        distance = 0
        for node in t1:
            if t1[node] != t2[node]:
                if nodes is None or node in nodes:
                    distance += 1
        return distance

    """ Sorts the array to maximize dissimilarity between test scenarios.
    """
    def maximizeDissimilarity(self, givenArray, nodes):
        if len(givenArray) == 1:
            return givenArray
        array = givenArray.copy()
        distanceMatrix = []
        bestScore = -1
        bestPair = (0, 0)
        index = 0
        for testCase in array:
            distances = [self.jaccardDistance(testCase, t, nodes) for t in array]
            if max(distances) > bestScore:
                bestScore = max(distances)
                bestPair = (index, distances.index(bestScore))
            index += 1
            distanceMatrix += distances
        # print("Most dissimilar test cases: " + str(bestPair) + " ; with score : " + str(bestScore))
        newArray = [array[bestPair[0]], array[bestPair[1]]]
        array.remove(array[max(bestPair)])
        array.remove(array[min(bestPair)])
        prevTest = newArray[1]
        collision = 0

        while array:  # until all test cases are transferred
            maxScore = self.jaccardDistance(array[0], prevTest, nodes)
            bestTestCase = array[0]
            for testCase in array:
                currentScore = self.jaccardDistance(testCase, prevTest, nodes)
                if currentScore == maxScore:
                    collision += 1
                if currentScore > maxScore:
                    maxScore = currentScore
                    bestTestCase = testCase

            prevTest = bestTestCase
            newArray.append(prevTest)
            array.remove(prevTest)

        # print("The number of collisions encountered while sorting is: " + str(collision))
        return newArray

    """Returns the distance between t1 and t2, only for features/contexts contained in nodes.
    """
    def jaccardDistance(self, t1, t2, nodes):
        intersection = 0
        for node in nodes:
            if t1[node] > 0 and t1[node] == t2[node]:
                intersection += 1
        union = 0
        for node in nodes:
            if t1[node] > 0 or t2[node] > 0:
                union += 1
        return 1 - intersection/union

    def maximizeReusability(self, suite):
        orderedSuite = suite.copy()
        reusabilitydegrees = {}
        numberOfTests = len(suite)
        for feature in self.features:
            degree = 0
            for test in suite:
                if test[feature] > 0:
                    degree += 1
            reusabilitydegrees[feature] = float(degree) / numberOfTests

    def getMinTestSuite(self):
        return self.suiteMinimized

    def getMaxTestSuite(self):
        return self.suiteMaximized

    def getRandomTestSuite(self):
        return self.suiteRandomOrder

    def getUnorderedTestSuite(self):
        return self.suiteUnordered

    def getLength(self):
        return len(self.suiteUnordered)

    def getSpecificOrderSuite(self, mode):
        if mode == "minimized":
            return self.suiteMinimized
        elif mode == "dissimilarity":
            return self.suiteMaximized
        elif mode == "unordered":
            return self.suiteUnordered
        elif mode == "random":
            return self.suiteRandomOrder
        print("MODE NOT RECOGNIZED: "+str(mode))
        return None

    def getCost(self, mode="unordered"):
        suite = self.getSpecificOrderSuite(mode)
        cost = 0
        prevTest = suite[0]
        for t in suite[1:]:
            cost += self.effortDistance(prevTest, t)
            prevTest = t
        return cost

    def printLatexTransitionForm(self, mode):
        suite = self.getSpecificOrderSuite(mode)
        prevTest = {f: -1*abs(suite[0][f]) for f in self.features+self.contexts if f != "Context" and f != "Feature"}
        num = 0
        for test in suite:
            num += 1
            linePlusContext = ""
            lineMinusContext = ""
            linePlusFeature = ""
            lineMinusFeature = ""
            for f in prevTest:
                if test[f] != prevTest[f]:
                    # sign = ", -" if test[f] < 0 else ", +"
                    if f in self.features:
                        if test[f] > 0:
                            linePlusFeature += ", +"+str(f)
                        else:
                            lineMinusFeature += ", -"+str(f)
                    else:
                        if test[f] > 0:
                            linePlusContext += ", +"+str(f)
                        else:
                            lineMinusContext += ", -"+str(f)
            if len(lineMinusContext) < 2:
                linePlusContext = linePlusContext[2:]
            if len(lineMinusFeature) < 2:
                linePlusFeature = linePlusFeature[2:]

            toPrint = str(num) + " & " + lineMinusContext[2:] + linePlusContext + " & " + lineMinusFeature[2:] + linePlusFeature + " \\\\\\hline"
            toPrint = toPrint.replace("Instructions", "Instr")
            print(toPrint)
            prevTest = test

def singleTest():
    time1 = time.time()
    models = "./data/enlarged/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    result = CITSAT(s, False, 30)
    # print(result)
    totalTime = time.time() - time1
    testSuite = TestSuite(s, result)
    result = testSuite.getMinTestSuite()
    print("==================== To create a Latex table ====================")
    printCoveringArray(result, s, mode="Refined", latex=True)
    print("\n")
    print("==================== Normal version ====================")
    printCoveringArray(result, s, mode="Refined", latex=False)

    print("Computation time : " + str(totalTime) + " seconds")

    unrefinedCost = numberOfChangements(testSuite.getMaxTestSuite(), s.getContexts())
    print("COST UNREFINED : " + str(unrefinedCost))
    refinedCost = numberOfChangements(testSuite.getMinTestSuite(), s.getContexts())
    print("COST REFINED : " + str(refinedCost))
    print("Decrease in cost of : " + str((unrefinedCost - refinedCost)/unrefinedCost))

    testSuite.compareFeatureSwitches()

    testSuite.findConfiguration(10)


def allPairs(systemData, filtered=True):
    mySATsolver = SATSolver(systemData)
    valuesForFactors = systemData.getValuesForFactors()
    unCovSets = []
    factors = list(valuesForFactors.keys())
    for i in range(len(factors) - 1):
        for j in range(len(valuesForFactors[factors[i]])):
            pair1 = (factors[i], valuesForFactors[factors[i]][j])
            for i2 in range(i + 1, len(factors)):
                for j2 in range(len(valuesForFactors[factors[i2]])):
                    pair2 = (factors[i2], valuesForFactors[factors[i2]][j2])

                    if mySATsolver.checkSAT([pair1[1], pair2[1]]):
                        # Each set is a [Factor, Value, Factor, Value, ...] tuple
                        unCovSets.append([pair1, pair2])
    if filtered:
        cores = []
        for candidate in list(valuesForFactors.keys()):
            if not mySATsolver.checkSAT([-1*abs(valuesForFactors[candidate][0])]):
                cores.append(candidate)
        unCovSets = [unCovSet for unCovSet in unCovSets if unCovSet[0][0] not in cores and unCovSet[1][0] not in cores]
    return unCovSets

def transitionExist(s):
    mySATsolver = SATSolver(s)
    valuesForFactors = s.getValuesForFactors()
    factors = list(valuesForFactors.keys())
    for i in range(len(factors) - 1):
        for j in range(len(valuesForFactors[factors[i]])):
            pair1 = (factors[i], valuesForFactors[factors[i]][j])
            for i2 in range(i + 1, len(factors)):
                for j2 in range(len(valuesForFactors[factors[i2]])):
                    pair2 = (factors[i2], valuesForFactors[factors[i2]][j2])

                    if mySATsolver.checkSAT([pair1[1], pair2[1]]) and mySATsolver.checkSAT([-1*pair1[1], -1*pair2[1]]):
                        return True
    return False


def allTransitions(s, filterForFeatures=True):
    pairs = allPairs(s)
    transitions = []
    for i in range(len(pairs)):
        pair = pairs[i]
        if filterForFeatures and (pair[0][0] not in s.getFeatures() or pair[1][0] not in s.getFeatures()):
            continue
        if findReversePair(pair, pairs):
            firstTransition = "+" if pair[0][1] > 0 else "-"
            firstTransition += pair[0][0]
            secondTransition = "+" if pair[1][1] > 0 else "-"
            secondTransition += pair[1][0]
            transitions.append((firstTransition, secondTransition))
    return transitions


def findReversePair(pair, pairs):
    for p in pairs:
        if p[0][1] == -1 * pair[0][1] and p[1][1] == -1 * pair[1][1]:
            return True
    return False


def testingScores():
    models = "../data/enlarged/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    resultsActivationOrder = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    resultsActivationCoverage = [0.0, 0.0, 0.0]
    nIterations = 5
    for i in range(nIterations):
        filepath = "../data/testSuitesSPLC/testSuite"+str(i)+".pkl"
        if os.path.exists(filepath):
            testSuite = readSuite(s, filepath)
        else:
            testSuite = TestSuite(s, CITSAT(s, False, 30))
            testSuite.storeSuite(filepath)

        currResult = testSuite.compareDistribution()
        for j in range(len(currResult)):
            resultsActivationOrder[j] += currResult[j]
        currResult = testSuite.analyseActivationCoverage()
        for j in range(len(currResult)):
            resultsActivationCoverage[j] += currResult[j]
    for j in range(len(resultsActivationOrder)):
        resultsActivationOrder[j] = resultsActivationOrder[j] / nIterations
    for j in range(len(resultsActivationCoverage)):
        resultsActivationCoverage[j] = resultsActivationCoverage[j] / nIterations

    print("-------------------------------------------")
    print("Unordered suite metrics, average on " + str(nIterations) + " tests:")
    print("Number of features: " + str(resultsActivationOrder[0])
          + "; number of tests: " + str(resultsActivationOrder[1])
          + "; average: " + str(resultsActivationOrder[2])
          + "; test score: " + str(resultsActivationOrder[3]))
    print("Coverage (number of pairs tested): " + str(resultsActivationCoverage[0]))

    print("Ordered suite metrics, average on " + str(nIterations) + " tests:")
    print("Number of features: " + str(resultsActivationOrder[4])
          + "; number of tests: " + str(resultsActivationOrder[5])
          + "; average: " + str(resultsActivationOrder[6])
          + "; test score: " + str(resultsActivationOrder[7]))
    print("Coverage (number of pairs tested): " + str(resultsActivationCoverage[1]))

    print("On average, decrease of " + str(resultsActivationCoverage[2]) + "% in the coverage.")


def randomSamplingCoverage():
    models = "./data/enlarged/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    testSuite = randomSampling(s)
    pairs = allPairs(s)
    maxCoverage = len(pairs)
    randomCoverage = computeCoverage(pairs, testSuite)
    print("Maximum coverage: "+str(maxCoverage) + "; coverage of random sampling: " + str(randomCoverage) + " - "+str(float(randomCoverage)/maxCoverage))
    print("Chance of generating valid test cases:")
    invalidChance(s)


if __name__ == '__main__':
    print("-------------------------------------------")
    # randomSamplingCoverage()
    testingScores()
    # testSuite.analyseActivationCoverage()
