import re


class SystemData:
    def __init__(self, contextsFile=None, featuresFile=None, mappingFile=None, extraConstraints=None):
        """if featuresFile is None:
            featuresFile = 'features.txt'
        if contextsFile is None:
            contextsFile = 'contexts.txt'
        if mappingFile is None:
            mappingFile = 'mapping.txt'"""

        # Read files for nodes
        self.features = []
        self.initFeatures(featuresFile)
        self.contexts = []
        self.initContexts(contextsFile)

        # Read file for constraints
        self.featureConstraints = []
        self.initFeatureConstraint(featuresFile)

        self.contextConstraints = []
        self.initContextConstraint(contextsFile)

        self.finalNodes = ['dummy', 'TreeRoot'] + list(self.contexts) + list(self.features)

        if "Feature" not in self.finalNodes:
            print("WARNING: The root of your feature model should always be \"Feature\".")
        if "Context" not in self.finalNodes and contextsFile is not None:
            print("WARNING: The root of your context model should always be \"Context\".")

        for feature in self.features:
            if feature in self.contexts:
                print("WARNING: the feature \"" + feature + "\" is also in the context model. You can't have a feature and a context with the exact same names.")

        # Read mapping file
        self.mappingConstraints = []
        self.initMapping(mappingFile)

        # Read extra constraints
        self.extraConstraints = []
        self.initExtraConstraints(extraConstraints)

        # We add a 'dummy' because a SAT solver begins at 1
        self.allConstraints = [('root', 'TreeRoot', [''])]\
                              + self.featureConstraints + self.contextConstraints + self.mappingConstraints

        # This is the data structure CITSAT.py uses
        self.valuesForFactors = {}
        index = 1
        for node in self.finalNodes[1:]:
            self.valuesForFactors[node] = [index, -index]
            index += 1

    def initFeatures(self, featureFile):
        if featureFile is None:
            # print("No features provided.")
            self.features = []
        else:
            f = open(featureFile, "r").readlines()
            self.features = set()
            for line in f:
                index = 0
                for feature in re.split("[\-/]", line):
                    if index == 1 and feature.lower() not in ["mandatory", "optional", "or", "alternative"]:
                        print("WARNING: In your feature model file, line: " + line + "does not seem to define a relationship.")
                    if index != 1:
                        self.features.add(feature.replace("\n", ""))
                    index += 1

    def initContexts(self, contextsFile):
        if contextsFile is None:
            # print("No contexts provided.")
            self.contexts = []
        else:
            f = open(contextsFile, "r").readlines()
            self.contexts = set()
            for line in f:
                index = 0
                for context in re.split("[\-/]", line):
                    if index == 1 and context.lower() not in ["mandatory", "optional", "or", "alternative"]:
                        print("WARNING: In your context model file, line: " + line + "\"does not seem to define a relationship.")
                    if index != 1:
                        self.contexts.add(context.replace("\n", ""))
                    index += 1

    def initFeatureConstraint(self, featuresFile):
        if featuresFile is None:
            print("No constraints provided for features.")
            self.featureConstraints = []
        else:
            f = open(featuresFile, "r").readlines()
            self.featureConstraints = [('root', 'Feature', [])]
            for line in f:
                parsedLine = line.replace("\n", "").split("/")
                if len(parsedLine) != 3:
                    print("In line \"" + str(line) + "\", the constraint is not correctly formatted.")
                newConstraint = (parsedLine[1], parsedLine[0], parsedLine[2].split("-"))
                self.featureConstraints.append(newConstraint)

    def initContextConstraint(self, contextFile):
        if contextFile is None:
            self.contextConstraints = []
        else:
            f = open(contextFile, "r").readlines()
            self.contextConstraints = [('root', 'Context', [])]
            for line in f:
                parsedLine = line.replace("\n", "").split("/")
                if len(parsedLine) != 3:
                    print("In line \"" + str(line) + "\", the constraint is not correctly formatted.")
                newConstraint = (parsedLine[1], parsedLine[0], parsedLine[2].split("-"))
                self.contextConstraints.append(newConstraint)

    def initMapping(self, mappingFile):
        if mappingFile is None:
            # print("No mapping provided.")
            self.mappingConstraints = []
        else:
            f = open(mappingFile, "r").readlines()
            activatesFeature = {}
            for line in f:
                line = line.rstrip("\n")
                if len(line.split('-ACTIVATES-')) < 2:
                    print("Error reading a file in the mapping: missing keyword ACTIVATES in line : " + str(line))

                m_features = line.split('-ACTIVATES-')[1].split('-')
                m_contexts = line.split('-ACTIVATES-')[0].split('-')
                #for c in m_contexts:
                #    self.mappingConstraints.append(('mandatory', c, m_features))

                # Verification that the mapping's features and contexts do exist.
                for feature in m_features:
                    if feature not in self.finalNodes:
                        print("WARNING: In the mapping, feature \"" + feature + "\" was not found in the feature model.")
                        print("Be careful to typos between both files (it is case sensitive).")
                        print("Be careful to spaces, especially at the end of a line containing this feature, both in the feature and mapping files.")

                for context in m_contexts:
                    if context not in self.finalNodes:
                        print("WARNING: In the mapping, context \"" + context + "\" was not found in the context model.")
                        print("Be careful to typos between both files (it is case sensitive).")
                        print("Be careful to spaces, especially at the end of the line containing this context, both in the context and mapping files.")

                for f in m_features:
                    if f not in activatesFeature:
                        activatesFeature[f] = []
                    activatesFeature[f].append(m_contexts)

                    self.mappingConstraints.append(('onePositiveRawClause', f, m_contexts))
                    #if len(m_contexts) > 1:
                    #    for c in m_contexts:
                    #       self.mappingConstraints.append(('onePositiveRawClause', c, [f]))
            for feature in activatesFeature:
                contextsClauses = [[]]
                for contexts in activatesFeature[feature]:
                    newContextsClauses = []
                    for clause in contextsClauses:
                        for context in contexts:
                            clauseCopy = clause.copy()
                            clauseCopy.append(context)
                            newContextsClauses.append(clauseCopy)
                    contextsClauses = newContextsClauses
                for clause in contextsClauses:
                    self.mappingConstraints.append(('oneNegativeRawClause', feature, clause))

    def toIndex(self, node):
        if isinstance(node, str):
            if node in self.finalNodes:
                return self.finalNodes.index(node)
            else:
                # For example, the Root constraint does not contain any child features, he will search an empty string.
                return 'VoidFeature'
        else:
            return [self.toIndex(f) for f in node]

    def getFeatures(self):
        return list(self.features.copy())

    def getContexts(self):
        return list(self.contexts.copy())

    def getNodes(self):
        return self.finalNodes.copy()

    def getConstraints(self):
        return self.allConstraints.copy()

    def getValuesForFactors(self):
        return self.valuesForFactors.copy()

    def getMappingConstraints(self):
        return self.mappingConstraints.copy()

    def getCNFConstraints(self):
        return self.extraConstraints.copy()

    def initExtraConstraints(self, extraConstraints):
        if extraConstraints is None:
            # print("No extra constraints provided.")
            self.extraConstraints = []
        else:
            f = open(extraConstraints, "r").readlines()
            for line in f:
                clause = [c.strip() for c in line.replace("~", "-").split("or")]
                newClause = []
                for c in clause:
                    newC = None
                    if c[0] == '-':
                        newC = -1
                        newC *= (self.toIndex(c[1:]))
                    else:
                        newC = self.toIndex(c)
                    newClause.append(newC)
                self.extraConstraints.append(newClause)
