from SATSolver import SATSolver
import random


def randomTestCase(valuesForFactors, satSolver):
    features = list(valuesForFactors.keys())
    random.shuffle(features)
    testCase = {}
    for f in features:
        testCase[f] = random.choice(valuesForFactors[f])
        sat = satSolver.checkSAT(testCase.values())
        if not sat:
            testCase[f] = -testCase[f]
    return testCase


def randomSampling(systemData):
    mySATsolver = SATSolver(systemData)
    valuesForFactors = systemData.getValuesForFactors()
    testSuite = []
    for i in range(18):
        newTestCase = randomTestCase(valuesForFactors, mySATsolver)
        testSuite.append(newTestCase)
    return testSuite


def computeCoverage(pairs, testSuite):
    coverPairsCount = 0
    for pair in pairs:
        if containsPair(pair, testSuite):
            coverPairsCount += 1
    return coverPairsCount


def containsPair(pair, testSuite):
    f1 = pair[0][0]
    v1 = pair[0][1]
    f2 = pair[1][0]
    v2 = pair[1][1]
    for testCase in testSuite:
        if testCase[f1] == v1 and testCase[f2] == v2:
            return True
    return False


def invalidChance(systemData):
    valuesForFactors = systemData.getValuesForFactors()
    mySatSolver = SATSolver(systemData)
    iterations = 1000000
    score = 0
    for i in range(iterations):
        testCase = {}
        for f in valuesForFactors:
            testCase[f] = random.choice(valuesForFactors[f])
        if mySatSolver.checkSAT(testCase.values()):
            score += 1
    print(str(iterations) + " test cases, "+ str(score) + " valid cases.")
