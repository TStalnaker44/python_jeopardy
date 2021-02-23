import pygame, copy, random, os
from enum import Enum
from polybius.graphics import *
from polybius.utils.timer import Timer
from uiManager import USER_INTERFACE
import jeopardy
from questioncard import QuestionCard
from polybius.managers import SOUNDS

class GameRound(Enum):
    JeopardyRound  = "jeopardy"
    DoubleJeopardy = "double_jeopardy"
    FinalJeopardy  = "final_jeopardy"

class JeopardyGameGUI():

    def __init__(self, fileName, answerTime, dims):

        self._dims   = dims
        self._width  = dims[0]
        self._height = dims[1]

        self.loadBackground()
        
        self._gameRound = GameRound.JeopardyRound

        self._game = jeopardy.JeopardyGame(fileName)
        self._cats, self._categoryMenu = self.prepareBoard()

        self._questionCard = None
        self._answerCard = None
        self._finalCatCard = None
        self._dailyDouble = None

        self.initializeTimer(answerTime)

        self._questionCounter = 0

        self.setDailyDoubles()

    def draw(self, screen):
        self._background.draw(screen)
        self.drawGameElements(screen)

    def handleEvent(self, event):
        self.loadQuestionOnClick(event)           
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.handleNextSlide()

    def update(self, ticks):
        self.updateRounds()
        SOUNDS.manageSongs("main")
        if self._dailyDouble == None and self._questionCard != None:
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
                                         barColor = (107,175,236))

    def prepareBoard(self):
        # Create the jeopardy board
        jeopardy_commands = USER_INTERFACE.getControlsForMenu(self._gameRound.value)
        cats = []
        tileWidth = self._width // 6.5
        start_x = self._width // 2 - (tileWidth*3)
        for i, x in enumerate(range(6)):
            cats.append(Menu((start_x + (tileWidth*i),150),(tileWidth, 500), jeopardy_commands, padding=(2,2), spacing=2,
                         color=(0,0,0), borderWidth=0, orientation="vertical"))

        # Create the category headers
        cat_template = {"color":(6, 12, 233), "font":"futura bold", "fontColor":(255, 255, 255),
                       "borderColor":(0,0,0), "borderWidth":1, "closeOnPress":False, "fontSize":28}
        category_commands = []
        if self._gameRound == GameRound.JeopardyRound:
            gameRound = self._game.getJeopardyRound()
        elif self._gameRound == GameRound.DoubleJeopardy:
            gameRound = self._game.getDoubleJeopardyRound()
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
        if self._dailyDouble != None:
            self._dailyDouble = None
        elif self._answerCard != None:
            self._answerCard = None
            # Increment the number of questions answered
            self._questionCounter += 1
        elif self._questionCard != None:
            self._questionCard = None
            self._answerCard = QuestionCard(self._answer, self._dims)
            self._answerCard.center(cen_point=(1/2,1/2))
        elif self._finalCatCard != None:
            self._question = formatCategoryText(self._game.getFinalJeopardyQuestion(), 30)
            self._answer = self._game.getFinalJeopardyAnswer()
            self._questionCard = QuestionCard(self._question, self._dims)
            self._questionCard.center(cen_point=(1/2,1/2))
            self._finalCatCard = None

    def loadQuestionOnClick(self, event):
        if self._questionCard == None and self._answerCard == None:
            for column, c in enumerate(self._cats):
               row = c.handleEvent(event)
               if row != None and c.getButtonByPosition(row-1)._text != "":
                  if self._gameRound == GameRound.JeopardyRound:
                     q_a = self._game.getQuestionsByCategory(self._game.getJeopardyRound()[column])[row-1]
                  elif self._gameRound == GameRound.DoubleJeopardy:
                     q_a = self._game.getQuestionsByCategory(self._game.getDoubleJeopardyRound()[column])[row-1]
                  self._question = formatCategoryText(q_a[0], 30)
                  self._answer = formatCategoryText(q_a[1], 50)
                  if self.checkForDailyDouble(row, column):
                      self._dailyDouble = QuestionCard("Daily Double", self._dims)
                      self._dailyDouble.center(cen_point=(1/2,1/2))
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
