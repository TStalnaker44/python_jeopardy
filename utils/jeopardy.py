

import csv, random, os

class JeopardyGame():

    def __init__(self, fileName):

        # Get the categories for the game
        self._jq = JeopardyQuestions(fileName)
        categories = self._jq.getGameCategories()
        random.shuffle(categories)
        self._jeopardyRound  = categories[:6]
        self._doubleJeopardy = categories[6:]
        self._finalJeopardy = self._jq.getFinalJeopardy()
        
        # Get the questions for the first round
        catDict = self._jq.jeopardyCategories()
        self._jeopardyQuestions = {}
        for c in self._jeopardyRound: 
            qa_list = catDict[c]
            self._jeopardyQuestions[c] = []
            while len(self._jeopardyQuestions[c]) < 5:
                temp = random.choice(qa_list)
                if not temp in self._jeopardyQuestions[c]:
                    self._jeopardyQuestions[c].append(temp)

        # Get the questions for the double jeopardy round
        catDict = self._jq.jeopardyCategories()
        for c in self._doubleJeopardy: 
            qa_list = catDict[c]
            self._jeopardyQuestions[c] = []
            while len(self._jeopardyQuestions[c]) < 5:
                temp = random.choice(qa_list)
                if not temp in self._jeopardyQuestions[c]:
                    self._jeopardyQuestions[c].append(temp)


    def getJeopardyRound(self):
        return self._jeopardyRound

    def getDoubleJeopardyRound(self):
        return self._doubleJeopardy

    def getQuestionsByCategory(self, c):
        return self._jeopardyQuestions[c]

    def getFinalJeopardyCatagory(self):
        return self._finalJeopardy[0]

    def getFinalJeopardyQuestion(self):
        return self._finalJeopardy[1]

    def getFinalJeopardyAnswer(self):
        return self._finalJeopardy[2]

class JeopardyQuestions():

    def __init__(self, fileName):

        self._jeopardyRound = {}
        self._finalJeopardy = []

        path = os.path.join("questions",fileName + ".csv")
        try: self.readFromFile('cp1252', path)
        except: self.readFromFile('utf-8', path)
            
        self._categories = [k for k in self._jeopardyRound.keys() if len(self._jeopardyRound[k]) >= 5]


    def readFromFile(self, encoding, path):
        with open(path, encoding=encoding) as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                gameRound = row[2]
                category = row[3]
                question = row[5]
                answer = row[6]
                # Filter out questions with links to other sites
                if question.find("<a href") == -1:
                    if gameRound == "Final Jeopardy!":
                        self._finalJeopardy.append((category, question, answer))     
                    else:
                        if category in self._jeopardyRound.keys():
                            self._jeopardyRound[category].append((question, answer))
                        else:
                            self._jeopardyRound[category] = [(question, answer)]

    def getCategory(self):
        return random.choice(self._categories)

    def getGameCategories(self):
        categories = []
        while len(categories) < 12:
            c = self.getCategory()
            if not c in categories:
                categories.append(c)
        return categories

    def jeopardyCategories(self):
        return self._jeopardyRound

    def getFinalJeopardy(self):
        return random.choice(self._finalJeopardy)



##
##jq = JeopardyQuestions()
##print(jq.getCategory())
##print()
##for x in jq.getGameCategories():
##    print(x)
##
##jg = JeopardyGame()
        
