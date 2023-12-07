import os
import time
import numpy as np
from TestSuite import *


def howManyForFullCoverage(s, uncovTransitions, mode):
    models = "../data/RIS-FOP/"
    storage = models + "TestSuitesCIT/testSuite-"
    tempUncovTr = uncovTransitions.copy()
    tempChainTests = 0
    chainTests = []
    maxIterations = 10000
    iteration = 0
    while iteration < maxIterations:
        iteration += 1
        testSuite = computeCITSuite(storage, iteration, s)
        transitions = testSuite.transitionPairCoverage(mode)
        tempChainTests += 1
        for e in tempUncovTr:
            if e in transitions or (e[1], e[0]) in transitions:
                tempUncovTr.remove(e)

        if len(tempUncovTr) == 0:
            chainTests.append(tempChainTests)
            tempChainTests = 0
            tempUncovTr = uncovTransitions.copy()
    return round(sum(chainTests)/len(chainTests), 2), np.std(chainTests)

def findSuitableCITsuite(s, errors, search="stats", mode="random", verbose=True):
    models = "../data/RIS-FOP/"
    storage = models + "TestSuitesCIT/testSuite-"
    countValids = 0.0
    averageErrorFounds = []
    maxIterations = 1000
    lengths = 0
    iteration = 0
    while iteration < maxIterations:
        iteration += 1
        testSuite = computeCITSuite(storage, iteration, s)
        transitions = testSuite.transitionPairCoverage(mode)

        errorFound = float(len(errors))
        for e in errors:
            if e not in transitions and (e[1], e[0]) not in transitions:
                errorFound -= 1
        averageErrorFounds.append(errorFound/len(errors))
        """if errorFound/len(errors) > 0.83:
            print("------------------")
            testSuite.printLatexTransitionForm(mode)"""
        if errorFound == len(errors):
            countValids += 1
        lengths += len(testSuite.getSpecificOrderSuite(mode))
        #if len(testSuite.getSpecificOrderSuite(mode)) < 9 and len(testSuite.getSpecificOrderSuite(mode)) > 6:
        if (errorFound == 0 and search == "notContains") or (errorFound == len(errors) and search == "contains"):
            print("Found after " + str(iteration) + " iterations.")
            testSuite.printLatexTransitionForm(mode)
            return testSuite
    # print("Max iterations reached.")
    percentage = round(100.0*countValids/maxIterations, 2)
    if verbose:
        print("mode = "+str(mode) + " : " + str(percentage) + " % containing the transitions, average size of " + str(lengths/maxIterations))
    if search == "statsContain":
        return percentage
    elif search == "statsCoverage":
        if countValids > 0:
            print("FOUND SUITES WITH ALL TRANSITIONS?")
        averageErrorFounds = [a*100.0 for a in averageErrorFounds]
        index_max = averageErrorFounds.index(max(averageErrorFounds))
        #print("index max " + str(index_max))
        return round(sum(averageErrorFounds)/maxIterations, 2), np.std(averageErrorFounds), max(averageErrorFounds)
    print("MODE NOT RECOGNIZED")


models = "../data/RIS/"
s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
s = SystemData(featuresFile='../data/RIS-FOP/features.txt')

modes = ["unordered", "random", "dissimilarity", "minimized"]
"""print("-HIGH +LOW")
for mode in modes:
    findSuitableCITsuite(s, [("-High", "+Low")], search="statsContain", mode=mode)

print("-MAP +INSTRUCTIONS")
for mode in modes:
    findSuitableCITsuite(s, [("+Instructions", "-Map")], search="statsContain", mode=mode)

print("TWO TRANSITIONS")
for mode in modes:
    findSuitableCITsuite(s, [("-High", "+Low"), ("+Instructions", "-Map")], search="statsContain", mode=mode)

print("+HIGH +INSTRUCTIONSFLOODS")
for mode in modes:
    findSuitableCITsuite(s, [("+InstructionsFloods", "+High")], search="statsContain", mode=mode)"""

# print("TWO TRANSITIONS")
# findSuitableCITsuite(s, [("-High", "+Low"), ("+Instructions", "-Map")], search="notContains", mode="random")

allTransitions = allTransitions(s)
print("Number of valid transitions : " + str(len(allTransitions)))
"""print("Computing chance of finding a specific transition in a suite.")
percentages = [0, 0, 0, 0]
it = 5
for transition in allTransitions[0:it]:
    for mode in modes:
        percentages[modes.index(mode)] += findSuitableCITsuite(s, [transition], search="statsContain", mode=mode, verbose=False)
percentages = [p/it for p in percentages]
print("Averages: " + str(percentages))"""

print("Computing percentage of coverage in average.")
# av = 50
percentages = [0, 0, 0, 0]
stds = [0.0, 0.0, 0.0, 0.0]
maxis = []
for mode in modes:
    average, std, maxi = findSuitableCITsuite(s, allTransitions, search="statsCoverage", mode=mode, verbose=False)
    percentages[modes.index(mode)] += average
    stds[modes.index(mode)] += std
    maxis.append(maxi)

print("Average: " + str(percentages))
print("Std Deviation: " + str(stds))
print("Maximum coverages: " + str(maxis))

chains = []
chain_std = []
for mode in modes:
    chain, std = howManyForFullCoverage(s, allTransitions, mode)
    chains.append(chain)
    chain_std.append(std)
print("Average chains to achieve full coverage: " + str(chains))
print("Std dev to achieve full coverage: " + str(chain_std))



# [("-High", "+Low"), ("+Instructions", "-Map")]
# [("-High", "+Low")]
# [("+Instructions", "-Map")]
"""toPrint = ["T1", "T2", "T1 & T2"]
transitions = [[("-High", "+Low")], [("+Instructions", "-Map")], [("-High", "+Low"), ("+Instructions", "-Map")]]
for t in transitions:
    percentages = [0, 0, 0, 0]
    for mode in modes:
        percentages[modes.index(mode)] += findSuitableCITsuite(s, t, search="statsContain", mode=mode, verbose=False)
    print("Contains " + toPrint[transitions.index(t)] + ": " + str(percentages))"""

# printCoveringArray(testSuite.getMinTestSuite(), s, mode="Refined", latex=False)
# transitions = testSuite.transitionPairCoverageMinimised()
# for t in transitions:
#    print(t)

# Errors are:
# 1) Transition error, UI error : -Map +Instructions (upperA will be below instead of above).
# 2) Transition error, message-based error : -high+low (counter will be at 0 instead of 1).
# 3) Interaction error, error : +InstructionsColdWeather +InstructionsFloods
