"""
@author: Trevor Stalnaker, Justin Pusztay
File: main.py

The main loop for running Squirrel Simulator
"""

import pygame, copy
from polybius.graphics import *
from uiManager import USER_INTERFACE
import jeopardy
from questioncard import QuestionCard

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

def prepareBoard(boardType, game):
   # Create the jeopardy board
   jeopardy_commands = USER_INTERFACE.getControlsForMenu(boardType)
   cats = []
   for i, x in enumerate(range(6)):
      cats.append(Menu((50 + (200*i),150),(200, 500), jeopardy_commands, padding=(2,2), spacing=2,
                     color=(0,0,0), borderWidth=0, orientation="vertical"))

   # Create the category headers
   cat_template = {"color":(6, 12, 233), "font":"futura bold", "fontColor":(255, 255, 255),
                   "borderColor":(0,0,0), "borderWidth":1, "closeOnPress":False, "fontSize":28}
   category_commands = []
   if boardType == "jeopardy":
      gameRound = game.getJeopardyRound()
   elif boardType == "double_jeopardy":
      gameRound = game.getDoubleJeopardyRound()
   for category in gameRound:
      temp = copy.copy(cat_template)
      temp["text"] = formatCategoryText(category, 12)
      category_commands.append(temp)
   categoryMenu = Menu((50,50),(1200, 100), category_commands, padding=(2,2), spacing=4,
                     color=(0,0,0), borderWidth=0, orientation="horizontal")

   return (cats, categoryMenu)
         

def main():
   """
   Main loop for the program
   """
   # Initialize the module
   pygame.init()
   pygame.font.init()
   pygame.mixer.init()

   # Update the title for the window
   pygame.display.set_caption('Jeopardy!')
   
   # Get the screen
   screen = pygame.display.set_mode((1300,800)) #, pygame.FULLSCREEN)

   # Create an instance of the game clock
   gameClock = pygame.time.Clock()

   font = pygame.font.SysFont("Times New Roman", 20)

   USER_INTERFACE.setResourcePath("menuButtons.csv")

   background = Drawable("jeopardy_background.png", (0,0))
   background.scale(2)

   gameRound = "jeopardy"

   game = jeopardy.JeopardyGame()
   cats, categoryMenu = prepareBoard("jeopardy", game)

   questionCard = None
   answerCard = None
   finalCatCard = None

   questionCounter = 0

   RUNNING = True

   while RUNNING:

      #Increment the clock
      gameClock.tick()

      screen.fill((255,255,255))
      
      pygame.display.flip()

      # event handling, gets all event from the eventqueue
      for event in pygame.event.get():
         # only do something if the event is of type QUIT or K_ESCAPE
         if (event.type == pygame.QUIT):
            RUNNING = False

         if questionCard == None and answerCard == None:
            for column, c in enumerate(cats):
               row = c.handleEvent(event)
               if row != None and c.getButtonByPosition(row-1)._text != "":
                  if gameRound == "jeopardy":
                     q_a = game.getQuestionsByCategory(game.getJeopardyRound()[column])[row-1]
                  elif gameRound == "double_jeopardy":
                     q_a = game.getQuestionsByCategory(game.getDoubleJeopardyRound()[column])[row-1]
                  question = formatCategoryText(q_a[0], 30)
                  answer = q_a[1]
                  questionCard = QuestionCard(question)
                  questionCard.center(cen_point=(1/2,1/2))

                  # Remove the tile from the screen
                  c.getButtonByPosition(row-1).setText("")

                  
         if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if answerCard != None:
               answerCard = None
               # Increment the number of questions answered
               questionCounter += 1
            elif questionCard != None:
               questionCard = None
               answerCard = QuestionCard(answer)
               answerCard.center(cen_point=(1/2,1/2))
            elif finalCatCard != None:
               question = formatCategoryText(game.getFinalJeopardyQuestion(), 30)
               answer = game.getFinalJeopardyAnswer()
               questionCard = QuestionCard(question)
               questionCard.center(cen_point=(1/2,1/2))
               finalCatCard = None
               

         if questionCounter == 30:
            if gameRound == "jeopardy":
               cats, categoryMenu = prepareBoard("double_jeopardy", game)
               questionCounter = 0
               gameRound = "double_jeopardy"
            elif gameRound == "double_jeopardy":
               finalCatCard = QuestionCard("Final Jeopardy\n\n" + game.getFinalJeopardyCatagory())
               finalCatCard.center(cen_point=(1/2,1/2))
               questionCounter = 0

            
      #Calculate ticks
      ticks = gameClock.get_time() / 1000
                   
   #Close the pygame window and quit pygame
   pygame.quit()

if __name__ == "__main__":
    main()

