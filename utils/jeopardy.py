

import csv, random, os, json
from pathlib import Path

class JeopardyGame():

    def __init__(self, fileName):

        # Get the categories for the game
        self._jq = JeopardyQuestions(fileName)
        categories = self._jq.getGameCategories()
        if not self._jq.fixed_layout:
            random.shuffle(categories)
        self._jeopardyRound  = categories[:6]
        self._doubleJeopardy = categories[6:]
        self._finalJeopardy = self._jq.getFinalJeopardy()
        
        # Get the questions for the first round
        catDict = self._jq.jeopardyCategories()
        self._jeopardyQuestions = {}
        for c in self._jeopardyRound: 
            qa_list = catDict[c]
            self._jeopardyQuestions[c] = list(qa_list) if self._jq.fixed_layout else random.sample(qa_list, 5)

        # Get the questions for the double jeopardy round
        catDict = self._jq.jeopardyCategories()
        for c in self._doubleJeopardy: 
            qa_list = catDict[c]
            self._jeopardyQuestions[c] = list(qa_list) if self._jq.fixed_layout else random.sample(qa_list, 5)


    def snapshot(self):
        return {"first": self._jeopardyRound, "second": self._doubleJeopardy,
                "final": self._finalJeopardy, "questions": self._jeopardyQuestions,
                "values": {c: [self.getQuestionValue(c, i) for i in range(5)]
                           for c in self._jeopardyQuestions}}

    @classmethod
    def from_snapshot(cls, state):
        from types import SimpleNamespace
        game = cls.__new__(cls)
        game._jeopardyRound = state["first"]
        game._doubleJeopardy = state["second"]
        game._finalJeopardy = state["final"]
        game._jeopardyQuestions = {c: [tuple(q) for q in questions] for c, questions in state["questions"].items()}
        values = state["values"]
        fixed = all(v is not None for row in values.values() for v in row)
        game._jq = SimpleNamespace(fixed_layout=fixed, question_values={
            c: dict(zip(game._jeopardyQuestions[c], row)) for c, row in values.items()})
        return game

    def getJeopardyRound(self):
        return self._jeopardyRound

    def getDoubleJeopardyRound(self):
        return self._doubleJeopardy

    def getQuestionsByCategory(self, c):
        return self._jeopardyQuestions[c]

    def getQuestionValue(self, category, row):
        if self._jq.fixed_layout:
            return self._jq.question_values[category][self._jeopardyQuestions[category][row]]
        return None

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
        self.question_values = {}

        path = os.path.join("questions",fileName + ".csv")
        try:
            layout = json.loads(Path(path).with_suffix(".layout.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            layout = {}
        if not isinstance(layout, dict):
            raise ValueError("Game layout metadata must be a JSON object.")
        self.fixed_layout = layout.get("preserve_layout") is True
        self.title = layout.get("title") if isinstance(layout.get("title"), str) else None
        try:
            self.readFromFile('utf-8-sig', path)
        except UnicodeDecodeError:
            self._jeopardyRound.clear()
            self._finalJeopardy.clear()
            self.question_values.clear()
            self.readFromFile('cp1252', path)

        self._jeopardyRound = {category: list(dict.fromkeys(questions))
                              for category, questions in self._jeopardyRound.items()}
            
        self._categories = [k for k in self._jeopardyRound.keys() if len(self._jeopardyRound[k]) >= 5]
        if len(self._categories) < 12:
            raise ValueError("A game needs at least 12 categories with 5 different clues each.")
        if not self._finalJeopardy:
            raise ValueError("Add at least one Final Jeopardy! question to this CSV.")
        if self.fixed_layout:
            if len(self._jeopardyRound) != 12 or any(len(questions) != 5 for questions in self._jeopardyRound.values()):
                raise ValueError("A fixed-layout game needs exactly 12 columns of 5 clues.")
            for category, questions in self._jeopardyRound.items():
                if len({self.question_values[category][question] for question in questions}) != 5:
                    raise ValueError("Each fixed-layout column needs five different point values.")


    def readFromFile(self, encoding, path):
        with open(path, encoding=encoding) as file:
            reader = csv.reader(file, delimiter=",")
            for line_number, row in enumerate(reader, 1):
                if not row:
                    continue
                if len(row) < 7:
                    raise ValueError(f"CSV row {line_number} needs seven columns.")
                if line_number == 1 and row[2].strip().lower() == "round":
                    continue
                gameRound = row[2]
                category = row[3]
                question = row[5]
                answer = row[6]
                if not category.strip() or not question.strip() or not answer.strip():
                    raise ValueError(f"CSV row {line_number} needs a category, question, and answer.")
                # Filter out questions with links to other sites
                if question.find("<a href") == -1:
                    if gameRound == "Final Jeopardy!":
                        self._finalJeopardy.append((category, question, answer))     
                    else:
                        if category in self._jeopardyRound.keys():
                            self._jeopardyRound[category].append((question, answer))
                        else:
                            self._jeopardyRound[category] = [(question, answer)]
                        if self.fixed_layout:
                            try:
                                value = int(row[4].replace("$", "").replace(",", "").strip())
                            except ValueError:
                                raise ValueError(f"CSV row {line_number} needs a numeric point value.") from None
                            if value <= 0:
                                raise ValueError(f"CSV row {line_number} needs a positive point value.")
                            self.question_values.setdefault(category, {})[(question, answer)] = value

    def getCategory(self):
        return random.choice(self._categories)

    def getGameCategories(self):
        if self.fixed_layout:
            return list(self._categories)
        return random.sample(self._categories, 12)

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
        
