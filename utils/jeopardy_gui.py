import pygame, copy, random, os, hashlib, sqlite3, time
from enum import Enum
from polybius.graphics import *
from polybius.utils.timer import Timer
from .uiManager import USER_INTERFACE
from .jeopardy import JeopardyGame
from .questioncard import QuestionCard
from polybius.managers import SOUNDS
from .wagers import WagerMenu

class GameRound(Enum):
    JeopardyRound  = "jeopardy"
    DoubleJeopardy = "double_jeopardy"
    FinalJeopardy  = "final_jeopardy"

class JeopardyGameGUI():

    def __init__(self, fileName, answerTime, dims, multiplayer=None, progress=None, game_id=None, game_title=None, board=None):

        self._dims   = dims
        self._width  = dims[0]
        self._height = dims[1]
        self.multiplayer = multiplayer
        self.new_game_requested = False
        self._activeValue = 0
        self._finalJudged = 0
        self.progress = progress
        self.session_id = None
        self.game_id = game_id
        self.game_title = game_title or os.path.basename(fileName).replace("_", " ")
        self.progress_error = ""
        self._activeCategory = ""
        self._questionRaw = ""
        self._answerRaw = ""
        self.wager = None
        self._activeIsDailyDouble = False
        self._final_wagers = []

        self.checkpoint_error = ""
        self._revision = 0
        self._last_save = 0
        self._source = fileName
        self.loadBackground()
        
        self._gameRound = GameRound.JeopardyRound

        self._game = JeopardyGame.from_snapshot(board) if board is not None else JeopardyGame(fileName)
        if progress is not None and game_id is None:
            with open(os.path.join("questions", fileName + ".csv"), "rb") as stream:
                self.game_id = hashlib.sha256(stream.read()).hexdigest()
        if multiplayer is not None:
            multiplayer.on_start = self.startTracking
        self._cats, self._categoryMenu = self.prepareBoard()

        self._questionCard = None
        self._answerCard = None
        self._finalCatCard = None
        self._dailyDouble = None

        self.initializeTimer(answerTime)

        self._questionCounter = 0

        self.setDailyDoubles()

    def startTracking(self, names):
        if self.progress is not None and self.session_id is None:
            total = sum(len(self._game.getQuestionsByCategory(category)) for category in self._game.getJeopardyRound() + self._game.getDoubleJeopardyRound()) + 1
            self.session_id = self.progress.start_game(self.game_id, self.game_title, total, names or ["Solo"])

    def toggleMute(self):
        SOUNDS.toggleMute()
            
    def draw(self, screen):
        self._background.draw(screen)
        self.drawGameElements(screen)
        if self.multiplayer is not None:
            self.multiplayer.draw(screen, self)
        if self.wager is not None:
            self.wager.draw(screen)

    def isBoardVisible(self):
        return all(card is None for card in (self._dailyDouble, self._questionCard, self._answerCard, self._finalCatCard))

    def handleEvent(self, event):
        if self.wager is not None:
            amounts = self.wager.handle_event(event)
            if amounts is not None:
                self.wager = None
                if self._gameRound == GameRound.FinalJeopardy:
                    self._final_wagers = amounts
                    self.revealFinalQuestion()
                else:
                    self._activeValue = amounts[0]
                    self._dailyDouble = None
                    self._timer.resetTimer()
            return
        if self.multiplayer is not None and self.multiplayer.handle_event(event, self):
            return
        self.loadQuestionOnClick(event)           
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.handleNextSlide()

    def update(self, ticks):
        if self.wager is not None:
            return
        if self.multiplayer is not None and (self.multiplayer.setup_open or self.multiplayer.finished):
            return
        self.updateRounds()
        SOUNDS.manageSongs("main")
        if self._dailyDouble == None and self._questionCard != None \
           and self._gameRound != GameRound.FinalJeopardy:
            self._timer.update(ticks, self.timeOut)
        self._timerDisplay.setProgress(self._timer._timer)

    def timeOut(self):
        self._questionCard = None
        self._answerCard = QuestionCard(self._answer, self._dims)
        self._answerCard.center(cen_point=(1/2,1/2))

    def initializeTimer(self, answerTime):
        self._timer = Timer(answerTime)
        q = QuestionCard("", self._dims)
        length = (4*q.getWidth())//5
        pos = (self._width // 2 - length // 2, q.getPosition()[1] + q.getHeight() - 75)
        self._timerDisplay = ProgressBar(pos, length,
                                         self._timer._initialTime,
                                         self._timer._timer,
                                         height = 25,
                                         barColor = (107,175,236),
                                         alignment="center")

    def prepareBoard(self):
        # Create the jeopardy board
        jeopardy_commands = USER_INTERFACE.getControlsForMenu("jeopardy" if self._gameRound == GameRound.JeopardyRound else "double_jeopardy")
        if self._gameRound == GameRound.JeopardyRound:
            gameRound = self._game.getJeopardyRound()
        else:
            gameRound = self._game.getDoubleJeopardyRound()
        cats = []
        tileWidth = self._width // 6.5
        start_x = self._width // 2 - (tileWidth*3)
        for i, x in enumerate(range(6)):
            controls = copy.deepcopy(jeopardy_commands)
            for row, control in enumerate(controls):
                value = self._game.getQuestionValue(gameRound[i], row)
                if value is not None:
                    control["text"] = f"${value:,}"
            cats.append(Menu((start_x + (tileWidth*i),150),(tileWidth, 500), controls, padding=(2,2), spacing=2,
                         color=(0,0,0), borderWidth=0, orientation="vertical"))

        # Create the category headers
        cat_template = {"color":(6, 12, 233), "font":"futura bold", "fontColor":(255, 255, 255),
                       "borderColor":(0,0,0), "borderWidth":1, "closeOnPress":False, "fontSize":28}
        category_commands = []
        for category in gameRound:
            temp = copy.copy(cat_template)
            temp["text"] = formatCategoryText(category, 12)
            category_commands.append(temp)
        categoryMenu = Menu((start_x,50),(tileWidth*6, 100), category_commands, padding=(2,2), spacing=4,
                         color=(0,0,0), borderWidth=0, orientation="horizontal")

        return (cats, categoryMenu)

    def loadBackground(self):
        path = os.path.join("resources","images","jeopardy_background.png")
        self._background = Drawable(path, (0,0))
        self._background.scale(2)

    def setDailyDoubles(self):
        # Round, column, row
        firstDailyDouble  = (GameRound.JeopardyRound,random.randint(0,5),random.randint(0,4))
        secondDailyDouble = (GameRound.DoubleJeopardy,random.randint(0,5),random.randint(0,4))
        column = random.randint(0,5)
        row = random.randint(0,4)
        while column == secondDailyDouble[1] and row == secondDailyDouble[2]:
            column = random.randint(0,5)
            row = random.randint(0,4)
        self._dailyDoubles = [firstDailyDouble,secondDailyDouble,
                              (GameRound.DoubleJeopardy,column,row)]

    def drawGameElements(self, screen):
        if self._dailyDouble != None:
            self._dailyDouble.draw(screen)
        # Draw question card
        elif self._questionCard != None:
            self._questionCard.draw(screen)
            if self._gameRound != GameRound.FinalJeopardy:
                self._timerDisplay.draw(screen)
        # Draw answer to question
        elif self._answerCard != None:
            self._answerCard.draw(screen)
        # Draw final category card
        elif self._finalCatCard != None:
            self._finalCatCard.draw(screen)
        # Draw Jeopardy Board
        else:
            for c in self._cats:
                c.draw(screen)
            self._categoryMenu.draw(screen)

    def handleNextSlide(self):
        if self.wager is not None:
            return
        if self._dailyDouble != None:
            self._dailyDouble = None
        elif self._answerCard != None:
            if self.multiplayer is not None:
                self.resolveAnswer("skip")
                return
            self._answerCard = None
            # Increment the number of questions answered
            self._questionCounter += 1
        elif self._questionCard != None:
            self._questionCard = None
            self._answerCard = QuestionCard(self._answer, self._dims)
            self._answerCard.center(cen_point=(1/2,1/2))
        elif self._finalCatCard != None:
            if self.multiplayer is not None:
                players = [(name, score, 0, max(0, score)) for name, score in zip(self.multiplayer.names, self.multiplayer.scores)]
                self.wager = WagerMenu(self._dims, "Final Jeopardy wagers", self._game.getFinalJeopardyCatagory(), players)
            else:
                self.revealFinalQuestion()

    def revealFinalQuestion(self):
        self._activeValue = self._final_wagers[self.multiplayer.turn] if self._final_wagers else 0
        self._activeCategory = self._game.getFinalJeopardyCatagory()
        self._questionRaw = self._game.getFinalJeopardyQuestion()
        self._answerRaw = self._game.getFinalJeopardyAnswer()
        self._question = formatCategoryText(self._questionRaw, 30)
        self._answer = formatCategoryText(self._answerRaw, 50)
        self._questionCard = QuestionCard(self._question, self._dims)
        self._questionCard.center(cen_point=(1/2,1/2))
        self._finalCatCard = None

    def resolveAnswer(self, result):
        if self._answerCard is None:
            return
        completing = self._gameRound == GameRound.FinalJeopardy and self._finalJudged + 1 >= max(1, len(self.multiplayer.names))
        if self.progress is not None:
            respondent = "solo" if self.multiplayer.solo else str(self.multiplayer.turn)
            player = self.multiplayer.names[self.multiplayer.turn]
            rollback = (list(self.multiplayer.scores), self.multiplayer.turn, self.multiplayer.finished,
                        self._finalJudged, self._answerCard, self._questionCounter, self._activeValue)
            try:
                self.progress.record_answer(self.session_id, self._activeCategory, self._questionRaw,
                    self._answerRaw, respondent, player, result, complete=completing, checkpoint=self._apply_answer)
            except sqlite3.Error:
                (self.multiplayer.scores, self.multiplayer.turn, self.multiplayer.finished,
                 self._finalJudged, self._answerCard, self._questionCounter, self._activeValue) = rollback
                self.progress_error = "Could not save this result. Press your answer button again."
                return
            if not completing:
                self._revision += 1
            self.progress_error = ""
            self.checkpoint_error = ""
        else:
            self._apply_answer(result)

    def _apply_answer(self, result):
        self.multiplayer.score(result, self._activeValue)
        if self._gameRound == GameRound.FinalJeopardy:
            self._finalJudged += 1
            if self._finalJudged >= max(1, len(self.multiplayer.names)):
                self._answerCard = None
                self.multiplayer.finished = True
            else:
                self._activeValue = self._final_wagers[self.multiplayer.turn]
        else:
            self._answerCard = None
            self._questionCounter += 1

        return None if self.multiplayer.finished else self.snapshot()

    def snapshot(self):
        players = self.multiplayer
        wager = None if self.wager is None else {key: getattr(self.wager, key) for key in
            ("title", "category", "players", "index", "amounts", "value", "select_all", "error")}
        return {"version": 1, "source": self._source, "game_id": self.game_id,
                "title": self.game_title, "session_id": self.session_id, "revision": self._revision,
                "board": self._game.snapshot(), "round": self._gameRound.value,
                "counter": self._questionCounter, "daily_doubles": [(r.value, c, row) for r, c, row in self._dailyDoubles],
                "used": [(c, row) for c, menu in enumerate(self._cats) for row in range(5)
                         if menu.getButtonByPosition(row)._text == ""],
                "active_value": self._activeValue, "final_judged": self._finalJudged,
                "active_daily": self._activeIsDailyDouble, "final_wagers": self._final_wagers,
                "category": self._activeCategory, "question": self._questionRaw, "answer": self._answerRaw,
                "cards": [card is not None for card in (self._dailyDouble, self._questionCard, self._answerCard, self._finalCatCard)],
                "timer": self._timer._timer, "answer_time": self._timer._initialTime,
                "players": {"names": players.names, "scores": players.scores, "turn": players.turn, "solo": players.solo},
                "wager": wager}

    def save_checkpoint(self, force=False):
        if self.progress is None or self.session_id is None or self.multiplayer.setup_open or self.multiplayer.finished:
            return True
        if not force and time.monotonic() - self._last_save < 1:
            return True
        try:
            self.progress.save_checkpoint(self.snapshot())
        except sqlite3.Error:
            self.checkpoint_error = "Could not save this game. Keep it open and try again."
            return False
        self._revision += 1
        self._last_save = time.monotonic()
        self.checkpoint_error = ""
        return True

    @classmethod
    def from_checkpoint(cls, state, dims, progress, restart=False):
        from .localplayers import LocalPlayers
        if state["version"] != 1:
            raise ValueError("This saved game version is unsupported.")
        game = cls(state["source"], state["answer_time"], dims, LocalPlayers(dims),
                   progress, state["game_id"], state["title"], board=state["board"])
        players = game.multiplayer
        players.names = list(state["players"]["names"])
        players.solo = state["players"]["solo"]
        players.setup_open = False
        players.scores = [0] * len(players.names)
        players.turn = 0
        game._dailyDoubles = [(GameRound(r), c, row) for r, c, row in state["daily_doubles"]]
        pygame.key.stop_text_input()
        if restart:
            players.names = (["Player 1", "Player 2"] if players.solo else players.names) + [""] * 6
            players.names = players.names[:6]
            players.solo = False
            players.scores = []
            players.setup_open = True
            pygame.key.start_text_input()
            return game
        game.session_id = state["session_id"]
        game._revision = state["revision"]
        players.scores = list(state["players"]["scores"])
        players.turn = state["players"]["turn"]
        game._gameRound = GameRound(state["round"])
        game._cats, game._categoryMenu = game.prepareBoard()
        for c, row in state["used"]:
            game._cats[c].getButtonByPosition(row).setText("")
        game._questionCounter = state["counter"]
        game._activeValue = state["active_value"]
        game._finalJudged = state["final_judged"]
        game._activeIsDailyDouble = state["active_daily"]
        game._final_wagers = list(state["final_wagers"])
        game._activeCategory = state["category"]
        game._questionRaw, game._answerRaw = state["question"], state["answer"]
        game._question = formatCategoryText(game._questionRaw, 30)
        game._answer = formatCategoryText(game._answerRaw, 50)
        texts = ["Daily Double", game._question, game._answer,
                 "Final Jeopardy\n\n" + game._game.getFinalJeopardyCatagory()]
        for key, present, text in zip(("_dailyDouble", "_questionCard", "_answerCard", "_finalCatCard"), state["cards"], texts):
            card = QuestionCard(text, dims) if present else None
            if card is not None:
                card.center(cen_point=(1/2, 1/2))
            setattr(game, key, card)
        game._timer._timer = state["timer"]
        game._timerDisplay.setProgress(game._timer._timer)
        if state["wager"] is not None:
            w = state["wager"]
            game.wager = WagerMenu(dims, w["title"], w["category"], w["players"])
            for key, value in w.items():
                setattr(game.wager, key, value)
        return game

    def loadQuestionOnClick(self, event):
        if self.isBoardVisible() and self._gameRound != GameRound.FinalJeopardy:
            for column, c in enumerate(self._cats):
               row = c.handleEvent(event)
               if row != None and c.getButtonByPosition(row-1)._text != "":
                  self._activeValue = row * (200 if self._gameRound == GameRound.JeopardyRound else 400)
                  if self._gameRound == GameRound.JeopardyRound:
                     self._activeCategory = self._game.getJeopardyRound()[column]
                  elif self._gameRound == GameRound.DoubleJeopardy:
                     self._activeCategory = self._game.getDoubleJeopardyRound()[column]
                  q_a = self._game.getQuestionsByCategory(self._activeCategory)[row-1]
                  csv_value = self._game.getQuestionValue(self._activeCategory, row-1)
                  if csv_value is not None:
                      self._activeValue = csv_value
                  self._questionRaw, self._answerRaw = q_a
                  self._question = formatCategoryText(q_a[0], 30)
                  self._answer = formatCategoryText(q_a[1], 50)
                  if self.checkForDailyDouble(row, column):
                      self._dailyDouble = QuestionCard("Daily Double", self._dims)
                      self._dailyDouble.center(cen_point=(1/2,1/2))
                      self._activeIsDailyDouble = True
                      if self.multiplayer is not None:
                          turn = self.multiplayer.turn
                          score = self.multiplayer.scores[turn]
                          categories = self._game.getJeopardyRound() if self._gameRound == GameRound.JeopardyRound else self._game.getDoubleJeopardyRound()
                          multiplier = 200 if self._gameRound == GameRound.JeopardyRound else 400
                          highest = max(self._game.getQuestionValue(category, index) or (index + 1) * multiplier for category in categories for index in range(5))
                          player = (self.multiplayer.names[turn], score, 5, max(score, highest))
                          self.wager = WagerMenu(self._dims, "Daily Double wager", self._activeCategory, [player], self._activeValue)
                  else:
                      self._activeIsDailyDouble = False
                  self._questionCard = QuestionCard(self._question, self._dims)
                  self._questionCard.center(cen_point=(1/2,1/2))
                  
                  # Remove the tile from the screen
                  c.getButtonByPosition(row-1).setText("")

                  #Reset the timer
                  if self._gameRound != GameRound.FinalJeopardy:
                      self._timer.resetTimer()

    def checkForDailyDouble(self, row, column):
        return any([dd[0]==self._gameRound and dd[1]==column and dd[2]==(row-1) \
                                         for dd in self._dailyDoubles])
            
    def updateRounds(self):
        if self._questionCounter == 30:
            if self._gameRound == GameRound.JeopardyRound:
                self._gameRound = GameRound.DoubleJeopardy
                self._cats, self._categoryMenu = self.prepareBoard()
                self._questionCounter = 0
               
            elif self._gameRound == GameRound.DoubleJeopardy:
               self._gameRound = GameRound.FinalJeopardy
               self._activeValue = 0
               self._finalCatCard = QuestionCard("Final Jeopardy\n\n" + self._game.getFinalJeopardyCatagory(),
                                                 self._dims)
               self._finalCatCard.center(cen_point=(1/2,1/2))
               self._questionCounter = 0

def formatCategoryText(category, charPerLine):
   terms = category.split(" ")
   retString = ""
   charCount = 0
   for i, t in enumerate(terms):
      if charCount + len(t) > charPerLine:
         retString += "\n" + t
         charCount = len(t)
      else:
         if i != 0:
            retString += " "
         retString += t
         charCount += len(t) + 1
   return retString
