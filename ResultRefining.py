

"""Refines the received array. SystemData is used to retrieve the list of contexts/features.
If mode is "Normal", will return a semi-refined array.
If mode is "Refined", will refine the completely refined array.
"""
def printCoveringArray(arrayCopy, systemData, mode="Normal", writeMode=False, evolution = None, order=False, latex=False):
    # print("========== RESULTS =============")
    if len(arrayCopy) == 0:
        print('No test case found.')
        return
    nPrevTests = 0
    newNodes = []
    if evolution is not None:
        nPrevTests = evolution.getNumberPrevTests()
        newNodes = evolution.getNewNodes()
        print("The added nodes are : " + str(evolution.newNodes))

    array = arrayCopy.copy()
    features = systemData.getFeatures()
    contexts = systemData.getContexts()
    if order:
        array = orderArray(array, contexts, nPrevTests)
    coreContexts = systemData.getContexts()
    coreFeatures = systemData.getFeatures()
    for testCase in array:
        for c in coreContexts:
            if testCase[c] < 0:
                coreContexts.remove(c)
        for f in coreFeatures:
            if testCase[f] < 0:
                coreFeatures.remove(f)
    print('CORE CONTEXTS : ' + str(coreContexts))
    print('CORE FEATURES : ' + str(coreFeatures))
    cores = coreFeatures + coreContexts + ['TreeRoot']

    nTest = 1
    if mode == "Normal":
        for testCase in array:
            printCompleteTestCase(testCase, nTest, contexts, features, cores)
            nTest += 1
    elif mode == "Refined":
        prevTestCase = array[0]
        if latex:
            printLatexCompleteTestCase(prevTestCase, nTest, contexts, features, cores, newNodes)
        else:
            printCompleteTestCase(prevTestCase, nTest, contexts, features, cores)
        nTest += 1
        for testCase in array[1:nPrevTests]:
            if latex:
                printLatexRefinedTestCase(testCase, nTest, contexts, features, prevTestCase, newNodes)
            else:
                printRefinedTestCase(testCase, nTest, contexts, features, prevTestCase, newNodes)
            nTest += 1
            prevTestCase = testCase
        if nPrevTests > 0:
            print("---------------END OF THE REUSED TESTS--------------")
        temp = max(1, nPrevTests)
        for testCase in array[temp:]:
            if latex:
                printLatexRefinedTestCase(testCase, nTest, contexts, features, prevTestCase)
            else:
                printRefinedTestCase(testCase, nTest, contexts, features, prevTestCase)
            nTest += 1
            prevTestCase = testCase

        if nPrevTests > 0:
            print("NUMBER OF REUSED TESTS/TOTAL TESTS : " + str(nPrevTests) + " / " + str(nTest-1))
            modif = numberOfChangements(array[:nPrevTests], contexts, newNodes)
            print("MODIFICATIONS ON PREVIOUS TESTS : " + str(modif))
            print("TOTAL COST : " + str(modif + numberOfChangements(array[nPrevTests:], contexts)))

    elif mode == "DataCollection":
        print("NUMBER OF REUSED TESTS/TOTAL TESTS : " + str(nPrevTests) + " / " + str(nTest - 1))
        modif = sum([1 for n in array[0] if array[0][n] > 0 and n in newNodes])
        prevTestCase = array[0]
        for testCase in array[1:nPrevTests]:
            modif += sum([1 for n in testCase if testCase[n] > 0 and prevTestCase[n] < 0 and n in newNodes])
            modif += sum([1 for n in testCase if testCase[n] < 0 and prevTestCase[n] > 0 and n in newNodes])
            prevTestCase = testCase
        print("MODIFICATIONS ON PREVIOUS TESTS : " + str(modif))

    if writeMode:
        testFile = open("../testsFile.txt", 'w')
        allNodes = ""
        for node in systemData.getNodes()[1:]:
            allNodes += node + "-"
        testFile.write(allNodes + "\n")

        for testCase in array:
            newTestCase = ""
            for node in testCase:
                if testCase[node] > 0:
                    newTestCase += node + "-"
            testFile.write(newTestCase + "\n")


def printCompleteTestCase(testCase, nTest, contexts, features, cores):
    newLine = str(nTest) + ' ||| CONTEXTS : '
    newLine += str(
        [context for context in testCase if testCase[context] > 0 and context not in cores and context in contexts])
    newLine += '\n  ||| FEATURES : '
    newLine += str(
        [feature for feature in testCase if testCase[feature] > 0 and feature not in cores and feature in features])
    print(newLine)
    print('---------------------------------------------------------------------------------------------------------')

def printLatexCompleteTestCase(testCase, nTest, contexts, features, cores, newNodes = None):
    if newNodes is None or len(newNodes) == 0:
        newNodes = contexts + features
    newLine = str(nTest) + ' & '
    for context in testCase:
        if testCase[context] > 0 and context in contexts and context in newNodes:
            newLine += context + ', '
    newLine = newLine[:-2] + ' & & '
    for feature in testCase:
        if testCase[feature] > 0 and feature in features and feature in newNodes:
            newLine += feature + ', '
    newLine = newLine[:-2] + ' & \\\\\\hline '
    print(newLine)

def printLatexRefinedTestCase(testCase, nTest, contexts, features, prevTestCase, newNodes=None):
    if newNodes is None:
        newNodes = contexts + features
    added = False
    newLine = str(nTest) + ' & '
    for context in testCase:
        if testCase[context] > 0 and context in contexts and prevTestCase[context] < 0 and context in newNodes:
            newLine += context + ", "
            added = True

    if added:
        newLine = newLine[:-2]
    added = False
    newLine += ' & '
    for context in testCase:
        if testCase[context] < 0 and context in contexts and prevTestCase[context] > 0 and context in newNodes:
            newLine += context + ", "
            added = True

    if added:
        newLine = newLine[:-2]
    added = False
    newLine += ' & '
    for feature in testCase:
        if testCase[feature] > 0 and feature in features and prevTestCase[feature] < 0 and feature in newNodes:
            newLine += feature + ", "
            added = True

    if added:
        newLine = newLine[:-2]
    added = False
    newLine += ' & '
    for feature in testCase:
        if testCase[feature] < 0 and feature in features and prevTestCase[feature] > 0 and feature in newNodes:
            newLine += feature + ", "
            added = True
    if added:
        newLine = newLine[:-2]
    added = False
    print(newLine + "\\\\\\hline")

def printRefinedTestCase(testCase, nTest, contexts, features, prevTestCase, newNodes=None):
    if newNodes is None:
        newNodes = contexts + features
    newLine = str(nTest) + ' || DELETED CONTEXTS : '
    newLine += str([context for context in testCase if
                    testCase[context] < 0 and context in contexts and prevTestCase[context] > 0 and context in newNodes])
    newLine += '\n  || ADDED CONTEXTS : '
    newLine += str([context for context in testCase if
                    testCase[context] > 0 and context in contexts and prevTestCase[context] < 0 and context in newNodes])
    newLine += '\n  || DELETED FEATURES : '
    newLine += str([feature for feature in testCase if
                    testCase[feature] < 0 and feature in features and prevTestCase[feature] > 0 and feature in newNodes])
    newLine += '\n  || ADDED FEATURES : '
    newLine += str([feature for feature in testCase if
                    testCase[feature] > 0 and feature in features and prevTestCase[feature] < 0 and feature in newNodes])
    print(newLine)
    print('---------------------------------------------------------------------------------------------------------')


""" Sorts the array thanks to the distance definition in testDistance.
"""
def orderArray(givenArray, nodes, nPrevTests=0):
    array = givenArray.copy()
    prevTest = []
    newArray = []
    prevTest = []
    previousTestNumber = []
    if nPrevTests > 0:
        for i in range(nPrevTests):
            prevTest = array[0]
            newArray.append(prevTest)
            array.remove(prevTest)
    else:
        prevTest = min(array, key=lambda testCase: sum([1 for c in nodes if testCase[c] > 0]))
        newArray = [prevTest]
        array.remove(prevTest)

    while array:  # until all test cases are transferred
        prevTest = min(array, key=lambda testCase: testDistance(testCase, prevTest, nodes))
        newArray.append(prevTest)
        array.remove(prevTest)
    return newArray
    # array = sorted(array, key=lambda testCase: testCaseDistance(testCase, initialTest))


"""Returns the distance between t1 and t2, only for features/contexts contained in nodes.
"""
def testDistance(t1, t2, nodes=None):
    distance = 0
    for node in t1:
        if t1[node] != t2[node]:
            if nodes is None or node in nodes:
                distance += 1
    return distance


def parentConstraint(constraints, root):
    concernedConstraints = []
    for constraint in constraints:
        (_, p, _) = constraint
        if p == root:
            concernedConstraints.append(constraint)
    if len(concernedConstraints) == 0:
        return None
    return concernedConstraints


def numberOfChangements(testSuite, allContexts, newNodes=None):
    contexts = allContexts.copy()
    if newNodes is not None:
        contexts = [contxt for contxt in contexts if contxt in newNodes]
    else:
        variabilityContexts = []
        for testCase in testSuite:
            for c in contexts:
                if testCase[c] < 0:
                    contexts.remove(c)
                    variabilityContexts.append(c)
        contexts = variabilityContexts

    if testSuite is None or len(testSuite) == 0:
        return 0

    prevTestCase = testSuite[0]
    score = sum([1 for context in contexts if prevTestCase[context] > 0])
    for testCase in testSuite:
        score += sum([1 for context in contexts if testCase[context] < 0 and prevTestCase[context] > 0])
        score += sum([1 for context in contexts if testCase[context] > 0 and prevTestCase[context] < 0])
        prevTestCase = testCase

    return score

def addedCreationCost(array, contexts, nPrevTests):
    testSuite = orderArray(array, contexts, nPrevTests)
    prevTestCase = testSuite[nPrevTests-1]
    score = 0
    for testCase in testSuite[nPrevTests:]:
        score += sum([1 for context in contexts if testCase[context] < 0 and prevTestCase[context] > 0])
        score += sum([1 for context in contexts if testCase[context] > 0 and prevTestCase[context] < 0])
        prevTestCase = testCase

    return score
