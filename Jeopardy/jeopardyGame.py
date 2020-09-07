"""
@author: Trevor Stalnaker
File: main.py

The main loop for running Jeopardy Python Edition
"""

import pygame, copy
from polybius.graphics import *
from uiManager import USER_INTERFACE
import jeopardy
from questioncard import QuestionCard
from jeopardy_gui import JeopardyGameGUI


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

   USER_INTERFACE.setResourcePath("menuButtons.csv")

   game = JeopardyGameGUI()

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

         game.handleEvent(event)
            
      #Calculate ticks
      ticks = gameClock.get_time() / 1000
                   
   #Close the pygame window and quit pygame
   pygame.quit()

if __name__ == "__main__":
    main()

