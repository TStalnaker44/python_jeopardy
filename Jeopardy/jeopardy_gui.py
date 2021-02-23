import pygame, copy, random, os
from polybius.graphics import *
from uiManager import USER_INTERFACE
import jeopardy
from questioncard import QuestionCard

class JeopardyGameGUI():

    def __init__(self, fileName):

        path = os.path.join("resources","images","jeopardy_background.png")
        self._background = Drawable(path, (0,0))
        self._background.scale(2)

        self._gameRound = "jeopardy"

        self._game = jeopardy.JeopardyGame(fileName)
        self._cats, self._categoryMenu = self.prepareBoard()

        self._questionCard = None
        self._answerCard = None
        self._finalCatCard = None

        self._questionCounter = 0

        # Round, column, row
        firstDailyDouble  = ("jeopardy",random.randint(0,6),random.randint(0,5))
        secondDailyDouble = ("double_jeopardy",random.randint(0,6),random.randint(0,5))
        temp_x = random.randint(0,6)
        temp_y = random.randint(0,5)
        while temp_x == secondDailyDouble[1] and temp_y == secondDailyDouble[2]:
            temp_x = random.randint(0,6)
            temp_y = random.randint(0,5)
        self._dailyDoubles = [firstDailyDouble,secondDailyDouble,
                              ("double_jeopardy",temp_x,temp_y)]


    def draw(self, screen):

        # Draw the background
        self._background.draw(screen)

        # Draw the game elements
        if self._questionCard != None:
            self._questionCard.draw(screen)
        elif self._answerCard != None:
            self._answerCard.draw(screen)
        elif self._finalCatCard != None:
            self._finalCatCard.draw(screen)
        else:
            for c in self._cats:
                c.draw(screen)
            self._categoryMenu.draw(screen)

    def handleEvent(self, event):
        
        if self._questionCard == None and self._answerCard == None:
            for column, c in enumerate(self._cats):
               row = c.handleEvent(event)
               if row != None and c.getButtonByPosition(row-1)._text != "":
                  if self._gameRound == "jeopardy":
                     q_a = self._game.getQuestionsByCategory(self._game.getJeopardyRound()[column])[row-1]
                  elif self._gameRound == "double_jeopardy":
                     q_a = self._game.getQuestionsByCategory(self._game.getDoubleJeopardyRound()[column])[row-1]
                  self._question = formatCategoryText(q_a[0], 30)
                  self._answer = formatCategoryText(q_a[1], 50)
                  if any([dd[0]==self._gameRound and dd[1]==column and dd[2]==(row-1) \
                                         for dd in self._dailyDoubles]):
                      self._question = "Daily Double\n\n\n" + self._question
                  self._questionCard = QuestionCard(self._question)
                  self._questionCard.center(cen_point=(1/2,1/2))

                  # Remove the tile from the screen
                  c.getButtonByPosition(row-1).setText("")
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self._answerCard != None:
                self._answerCard = None
                # Increment the number of questions answered
                self._questionCounter += 1
            elif self._questionCard != None:
                self._questionCard = None
                self._answerCard = QuestionCard(self._answer)
                self._answerCard.center(cen_point=(1/2,1/2))
            elif self._finalCatCard != None:
                self._question = formatCategoryText(self._game.getFinalJeopardyQuestion(), 30)
                self._answer = self._game.getFinalJeopardyAnswer()
                self._questionCard = QuestionCard(self._question)
                self._questionCard.center(cen_point=(1/2,1/2))
                self._finalCatCard = None
               
        if self._questionCounter == 30:
            if self._gameRound == "jeopardy":
                self._gameRound = "double_jeopardy"
                self._cats, self._categoryMenu = self.prepareBoard()
                self._questionCounter = 0
               
            elif self._gameRound == "double_jeopardy":
               self._finalCatCard = QuestionCard("Final Jeopardy\n\n" + self._game.getFinalJeopardyCatagory())
               self._finalCatCard.center(cen_point=(1/2,1/2))
               self._questionCounter = 0



    def prepareBoard(self):
        # Create the jeopardy board
        jeopardy_commands = USER_INTERFACE.getControlsForMenu(self._gameRound)
        cats = []
        for i, x in enumerate(range(6)):
            cats.append(Menu((50 + (200*i),150),(200, 500), jeopardy_commands, padding=(2,2), spacing=2,
                         color=(0,0,0), borderWidth=0, orientation="vertical"))

        # Create the category headers
        cat_template = {"color":(6, 12, 233), "font":"futura bold", "fontColor":(255, 255, 255),
                       "borderColor":(0,0,0), "borderWidth":1, "closeOnPress":False, "fontSize":28}
        category_commands = []
        if self._gameRound == "jeopardy":
            gameRound = self._game.getJeopardyRound()
        elif self._gameRound == "double_jeopardy":
            gameRound = self._game.getDoubleJeopardyRound()
        for category in gameRound:
            temp = copy.copy(cat_template)
            temp["text"] = formatCategoryText(category, 12)
            category_commands.append(temp)
        categoryMenu = Menu((50,50),(1200, 100), category_commands, padding=(2,2), spacing=4,
                         color=(0,0,0), borderWidth=0, orientation="horizontal")

        return (cats, categoryMenu)

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
