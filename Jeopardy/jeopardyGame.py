"""
@author: Trevor Stalnaker
File: main.py

The main loop for running Jeopardy Python Edition
"""

import pygame, copy, os, argparse
from polybius.graphics import *
from utils.uiManager import USER_INTERFACE
from polybius.managers import SOUNDS
import utils.jeopardy, re
from utils.questioncard import QuestionCard
from utils.jeopardy_gui import JeopardyGameGUI

def main(fileName, answerTime, fullscreen, dims):
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

   #fullscreen = fullscreen.lower() == "true"
   
   # Get the screen
   if fullscreen:
      screen = pygame.display.set_mode(dims, pygame.FULLSCREEN)
   else:
      screen = pygame.display.set_mode(dims)

   # Create an instance of the game clock
   gameClock = pygame.time.Clock()

   USER_INTERFACE.setResourcePath(os.path.join("utils","menuButtons.csv"))

   if fileName.endswith(".csv"):
      fileName = fileName[:-4]
      
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

CONTROLS = """
Controls:

- Press the ESCAPE key or press the X to exit the game

- Hit the M key to mute and unmute game audio

- Click on Question Tiles to select them

   - The timer will begin automatically

- Click the Space Bar when the question has been answered to advance
   to the solution screen. 

   - The game will advance automatically when the timer runs out

- Click the Space Bar once more to advance from the Answer Screen
   back to the Game Board

- The game will automatically advance between rounds

- There is no functionality to keep track of scores
"""

if __name__ == "__main__":
   descStr = "A program that runs a Jeopardy Game with Jeopardy, Double Jeopardy, and Final Jeopardy Rounds"
   parser = argparse.ArgumentParser(description=descStr)
   parser.add_argument("-c, --controls", dest="controls", action="store_true", default=False,
     help="show game controls and exit")
   parser.add_argument("--questions", dest="qfile",
     default="JEOPARDY_CSV_REAL", type=str, required=False,
     help="the name of the CSV file that contains all of the questions and answers for the Jeopardy Game")
   parser.add_argument("--timer", dest="timer",
     default=30, type=int, required=False,
     help="the amount of time in seconds that players will have to answer questions")
   parser.add_argument("--fullscreen", dest="fullscreen", action="store_true", default=False,
     help="set the game to be rendered in full screen")
   parser.add_argument("--dims", dest="dims", type=str,
     default="(1200,800)", required=False,
     help="the width and height of the desired screen in pixels : Entered as (<width>, <height>)") 
   args = parser.parse_args()
   if not args.controls:
      main(args.qfile, args.timer, args.fullscreen, args.dims)
   else:
      print(CONTROLS)

