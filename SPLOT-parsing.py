from SystemData import SystemData
from TestSuite import *
from SATSolver import SATSolver


def writeTextFiles(filename):
    featureModel, constraints = getContents(filename)
    txtFilename = filename.replace("xml", "txt").replace("source", "txt")
    txtFile = open(txtFilename, "w")
    for index in range(len(featureModel) - 1):
        relations = getRelation(featureModel, index)
        for relation in relations:
            txtFile.write(relation + "\n")

    constraintFileName = filename.replace("xml", "txt").replace("source", "txtconstraints")
    constraintFile = open(constraintFileName, "w")

    for index in range(len(constraints)):
        constraint = getConstraint(constraints, index)
        constraintFile.write(constraint + "\n")


def filterOR(line):
    line = line.replace("connector", "connectr").replace("horizontal", "hrizotanl").replace("forward", "frward") \
        .replace("memory", "memry").replace("storage", "strage").replace("format", "frmat") \
        .replace("corporation", "crpration").replace("form", "frm").replace("organization", "rganization").replace(
        "source-oriented", "source-riented") \
        .replace("target-oriented", "target-riented").replace("dedicated support", "dedicated supprt").replace("sensor", "sensr")

    dictio = ["coroutine", "priority", "category", "more", "processor", "core", "history", "perform", "oracle"]
    for word in dictio:
        line = line.replace(word, word.replace("o", ""))

    return line


def getContents(filename):
    file = open(filename, "r")
    content = [filterOR(c.lower()) for c in file.readlines()]
    startFM = 0
    line = content[startFM]
    while line != "<feature_tree>\n":
        startFM += 1
        line = content[startFM]
    endFM = startFM
    while line != "</feature_tree>\n":
        endFM += 1
        line = content[endFM]
    featureModel = content[startFM + 1:endFM]

    root = findUniqueID(featureModel[0])
    if not alternative_ID:
        begin = featureModel[0].find("(")
        end = featureModel[0].find(")")
        featureModel[0] = featureModel[0][:begin + 1] + "Feature" + featureModel[0][end:]
    else:
        featureModel[0] = ":r Feature"

    startConstraint = endFM + 2
    constraints = []
    line = content[startConstraint].replace(" ", "").strip()
    while line != "</constraints>":
        if root in line:
            parts = line.split(":")
            conditions = parts[1].split("or")
            line = parts[0] + ":"
            for c in conditions:
                finalC = c
                if c[0] == "~":
                    finalC = c[1:]
                    line += "~"
                if finalC == root:
                    line += "Feature"
                else:
                    line += finalC
                line += "or"
            line = line[:-2]

        startConstraint += 1
        constraints.append(line)
        line = content[startConstraint].replace(" ", "").strip()

    return featureModel, constraints


def getConstraint(constraints, index):
    return constraints[index].split(":")[1]


def getRelation(featureModel, index):
    line = featureModel[index]
    parent = findUniqueID(line)
    if "or" in parent:
        print("RAISE ALERT : WORD OR IS FOUND IN UNIQUE ID : " + str(parent))
    relations = []

    level = line.count("\t")
    tempIndex = index + 1
    tempLine = featureModel[tempIndex]
    tempLevel = tempLine.count("\t")

    # this line is part of a group of feature, alt or or, which is already taken into account
    if tempLine.replace("\t", "")[:2] == ": ":
        return []

    while tempLevel > level and tempIndex < len(featureModel):
        if tempLevel == level + 1:
            relationType = tempLine.replace("\t", "")[:2]
            if relationType == ":o":
                relations.append(parent + "/Optional/" + findUniqueID(tempLine))
            elif relationType == ":m":
                relations.append(parent + "/Mandatory/" + findUniqueID(tempLine))
            elif relationType == ":g":
                relationType = "Alternative" if line[line.find("[") + 1:line.find("]")] == "1,1" else "Or"
                relation = parent + "/" + relationType + "/"
                orIndex = tempIndex + 1
                orLine = featureModel[orIndex]
                orLevel = orLine.count("\t")
                while orLevel > tempLevel and orIndex < len(featureModel):
                    if orLevel == tempLevel + 1:
                        if orLine.replace("\t", "")[:2] != ": ":
                            print("ERROR WHILE PARSING ALTERNATIVE/OR CONSTRAINTS.")
                        relation += findUniqueID(orLine) + "-"
                    orIndex += 1
                    if orIndex < len(featureModel):
                        orLine = featureModel[orIndex]
                    orLevel = orLine.count("\t")
                relations.append(relation[:-1])
            else:
                print("ERROR IN PARSING XML FILE. FOUND : " + str(relationType))
        tempIndex += 1
        if tempIndex < len(featureModel):
            tempLine = featureModel[tempIndex]
        tempLevel = tempLine.count("\t")
    return relations


def findUniqueID(line):
    if not alternative_ID:
        return line[line.find("(") + 1:line.find(")")]
    else:
        line = line.replace("\t", "")
        if ": " in line:
            line = line[2:].strip().replace("/", "").replace("-", "")
        else:
            line = line[3:].strip().replace("/", "").replace("-", "")
        if "(" in line and ")" in line:
            # if line[line.find("(") + 1:line.find(")")].strip() == line[:line.find("(")].strip():
            return line[line.find("(") + 1:line.find(")")].strip()
        return line.strip()


if __name__ == '__main__':
    # getSystemData("../data/SPLOT/SPLOT-source/SPLOT-3CNF-FM-500-50-1.00-SAT-10.xml")
    directory = "../data/SPLOT/SPLOT-source/"
    alternative_ID = False
    for filename in os.listdir(directory):
        if "REAL" in filename or "stack_fm" in filename:
            alternative_ID = True
        else:
            alternative_ID = False
        #if "REAL-FM-1.xml" in filename:
        f = os.path.join(directory, filename)
        writeTextFiles(f)
        # s = SystemData(featuresFile="../data/SPLOT/SPLOT-txt/TESTFILE.txt", extraConstraints="../data/SPLOT/SPLOT-txtconstraints/TESTFILE.txt")
        # solver = SATSolver(s)
