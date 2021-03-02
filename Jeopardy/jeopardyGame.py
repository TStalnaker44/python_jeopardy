"""
@author: Trevor Stalnaker
File: main.py

The main loop for running Jeopardy Python Edition
"""

import pygame, copy, os, sys
from polybius.graphics import *
from utils.uiManager import USER_INTERFACE
from polybius.managers import SOUNDS
import utils.jeopardy, re
from utils.questioncard import QuestionCard
from utils.jeopardy_gui import JeopardyGameGUI

def main(fileName="JEOPARDY_CSV_REAL", answerTime=30, dims="(1200,800)"):
   """
   Main loop for the program
   """

   # Initialize the module
   pygame.init()
   pygame.font.init()
   pygame.mixer.init()

   initializeManagers()

   # Update the title for the window
   pygame.display.set_caption('Jeopardy!')

   t = re.search("\((\d+),[ ]*(\d+)\)", dims)
   dims = (int(t.group(1)), int(t.group(2)))
   print(dims)
   
   # Get the screen
   screen = pygame.display.set_mode(dims)#, pygame.FULLSCREEN)

   # Create an instance of the game clock
   gameClock = pygame.time.Clock()

   USER_INTERFACE.setResourcePath(os.path.join("utils","menuButtons.csv"))

   

   game = JeopardyGameGUI(fileName, int(answerTime), dims)

   RUNNING = True

   while RUNNING:

      #Increment the clock
      gameClock.tick()

      screen.fill((255,255,255))

      game.draw(screen)
      
      pygame.display.flip()

      # event handling, gets all event from the eventqueue
      for event in pygame.event.get():
         # only do something if the event is of type QUIT or K_ESCAPE
         if (event.type == pygame.QUIT):
            RUNNING = False
         if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            RUNNING = False
         if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            game.toggleMute()

         game.handleEvent(event)
            
      #Calculate ticks
      ticks = gameClock.get_time() / 1000
      game.update(ticks)
                   
   #Close the pygame window and quit pygame
   pygame.quit()

def initializeManagers():
   SOUNDS.setResourcePath(os.path.join("resources","data","music.csv"))
   SOUNDS.setMusicFolderPath(os.path.join("resources","music"))

if __name__ == "__main__":
   main(*sys.argv[1:])

