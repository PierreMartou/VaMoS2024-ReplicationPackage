import math
import os
from SystemData import SystemData
from TestSuite import readSuite
import matplotlib.pyplot as plt
import numpy as np

def sizeOfModels(dataFolder):
    index = 0
    nFeatures = 0
    nContexts = 0
    nMapping = 0
    sizeSuite = 0
    for subdir, dirs, files in os.walk(dataFolder):
        if subdir != "./questionnaire_data" and subdir[-6:] == "_file_":
            index += 1
            subdir = subdir.replace("\\", "/")
            s = SystemData(subdir+'/contexts.txt', subdir+'/features.txt', subdir+'/mapping.txt')
            # print("Number of contexts: " + str(len(s.getContexts())) + " - Number of features: " + str(len(s.getFeatures())))
            # testSuite = TestSuite(s, CITSAT(s, False, 30))
            # testSuite.storeSuite(subdir+"/testSuite.pkl")
            testSuite = readSuite(s, subdir+"/testSuite.pkl")
            sizeSuite += len(testSuite.getMinTestSuite())
            nFeatures += len(s.getFeatures())
            nContexts += len(s.getContexts())
            test = open(subdir+'/mapping.txt')
            nMapping += len(test.readlines())
    return nFeatures / index, nContexts / index, sizeSuite / index, nMapping / index


def questionnairePie():
    y = np.array([35, 25, 25, 15])
    mylabels = ["Apples", "Bananas", "Cherries", "Dates"]

    plt.pie(y, labels = mylabels)
    plt.show()


def questionnairePlot(names, y, file_name):
    fig = plt.figure(figsize=(6.4, 4.8*len(names)/8))
    names.reverse()
    width = 0.5
    y.reverse()
    x = [i*0.7+1 for i in range(len(names))]
    plt.barh(x, y, width, color='#3864cc')#'#386cb0')

    new_y = range(0, math.ceil(max(y))+1, 2)
    if max(y) < 5:
        new_y = range(0, math.ceil(max(y))+1)

    plt.xticks(new_y)
    plt.yticks(x, names)
    plt.savefig(file_name, bbox_inches='tight')
    plt.show()


def questionnaireDesignCauses():
    names = ["Design fault", "Modelling of the env.", "Adaptation to the env.", "New ideas", "Other"]
    y = [13, 5, 9, 8, 5]
    filename = 'design-causes.png'
    questionnairePlot(names, y, filename)

def questionnaireDesignStrengths():
    names = ["U. the domain", "U. the modelling", "U. the implementation", "U. design testing", "U. implementation testing", "Correct the design", "Improve the design"]
    y = [8, 11, 3, 5, 3, 15, 12]
    filename = 'design-strengths.png'
    questionnairePlot(names, y, filename)

def questionnaireDesignWeaknesses():
    names = ["Use the suite", "Extract results", "Write usage scenarios", "Overkill to use the tool", "Other"]
    y = [0, 6, 4, 2, 10]
    filename = 'design-weaknesses.png'
    questionnairePlot(names, y, filename)

def questionnaireImplementationCauses():
    names = ["Declaration of\nthe context-feature model", "Application classes", "Feature behaviour", "System behaviour", "Interaction between features", "Interaction between\napplication classes and features", "Understanding of RubyCOP", "Other"]
    # names = ["a", "b", "c", "d", "d", "g", "d", "h"]
    y = [3, 0, 4, 2, 4, 3, 2, 2]
    filename = 'implementation-causes.png'
    questionnairePlot(names, y, filename)

def questionnaireImplementationDifficulties():
    names = ["Hard to use", "Tool didn't work as intended", "Already corrected\nwithout help", "Already corrected\nwith another tool", "Too simple models, overkill", "No difficulties", "Other"]
    y = [1, 2, 2, 1, 1, 13, 2]
    filename = 'implementation-difficulties.png'
    questionnairePlot(names, y, filename)

def questionnaireNumberOfDesignErrors():
    names = ["0 change", "1 change", "2 to 5 changes", "6 to 10 changes"]
    y = [1, 4, 13, 1]
    filename = "number-errors-design.png"
    questionnairePlot(names, y, filename)

def questionnaireNumberOfImplementationErrors():
    names = ["0 change", "1 change", "2 to 5 changes", "6 to 10 changes", "More than\n10 changes"]
    y = [10, 2, 4, 2, 1]
    filename = "number-errors-implementation.png"
    questionnairePlot(names, y, filename)


dataFolder = './questionnaire_data/student_models'
questionnaireNumberOfImplementationErrors()
questionnaireNumberOfDesignErrors()
# questionnaireDesignCauses()
# questionnaireDesignStrengths()
# questionnaireDesignWeaknesses()
# questionnaireImplementationCauses()
# questionnaireImplementationDifficulties()
# print(sizeOfModels(dataFolder))
