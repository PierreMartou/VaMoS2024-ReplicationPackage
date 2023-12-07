def alternativeConstraint(parent, children):
    newClauses = []
    lastClause = []
    for i in range(len(children)):
        currentChild = children[i]
        lastClause += [currentChild]
        for j in range(i + 1, len(children)):
            child = children[j]
            if child != currentChild:
                newClauses.append([-currentChild, -child])
        newClauses.append([-currentChild, parent])
    lastClause.append(-parent)
    newClauses.append(lastClause)
    return newClauses


def optionalConstraint(parent, children):
    newClauses = []
    for child in children:
        newClauses.append([-child, parent])
    return newClauses


def mandatoryConstraint(parent, children):
    newClauses = []
    for child in children:
        newClauses.append([child, -parent])
        newClauses.append([-child, parent])
    return newClauses


def orConstraint(parent, children):
    newClauses = []
    finalClause = [-parent]
    for child in children:
        newClauses.append([-child, parent])
        finalClause.append(child)
    newClauses.append(finalClause)
    return newClauses


def exclusionConstraint(parent, children):
    newClauses = []
    for child in children:
        newClauses.append([-parent, -child])
    return newClauses


# sources require target = if source is true, target should be true
def requirementConstraint(target, sources):
    newClauses = []
    for source in sources:
        newClauses.append([target, -source])
    return newClauses


def rootConstraint(target, sources=''):
    return [[target]]


def onePositiveRawClause(positive, negatives):
    clause = [positive]
    for negative in negatives:
        clause.append(-negative)
    return [clause]


def oneNegativeRawClause(negative, positives):
    clause = [-negative]
    for positive in positives:
        clause.append(positive)
    return [clause]


def exactClause(parent, clause):
    clauses = []

switcher = {
    'optional': optionalConstraint,
    'mandatory': mandatoryConstraint,
    'alternative': alternativeConstraint,
    'or': orConstraint,
    'exclusion': exclusionConstraint,
    'requirement': requirementConstraint,
    'root': rootConstraint,
    'onepositiverawclause': onePositiveRawClause,
    'onenegativerawclause': oneNegativeRawClause
}
