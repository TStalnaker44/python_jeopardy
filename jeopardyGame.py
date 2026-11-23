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
from utils.settings import SettingsMenu
from utils.localplayers import LocalPlayers
from pygame._sdl2.video import Window


def setDisplay(dims, fullscreen):
   # Recreate the SDL renderer when switching a scaled display's mode.
   pygame.display.quit()
   pygame.display.init()
   pygame.display.set_icon(pygame.image.load(os.path.join("resources", "images", "jeopardy_window_icon.png")))
   # Scale the board inside a normal window with native window controls.
   flags = pygame.SCALED | pygame.RESIZABLE
   screen = pygame.display.set_mode(dims, flags)
   if fullscreen:
      window = Window.from_display_module()
      window.maximize()
   pygame.display.set_caption('Jeopardy!')
   setWindowDarkMode()
   return screen

def setWindowDarkMode():
   """Use a dark native title bar without changing the Windows theme."""
   if os.name != "nt":
      return
   handle = pygame.display.get_wm_info().get("window")
   if not handle:
      return
   import ctypes
   from ctypes import wintypes
   try:
      set_attribute = ctypes.WinDLL("dwmapi").DwmSetWindowAttribute
      set_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
      set_attribute.restype = ctypes.c_long
      dark = ctypes.c_int(1)
      if set_attribute(handle, 20, ctypes.byref(dark), ctypes.sizeof(dark)) != 0:
         set_attribute(handle, 19, ctypes.byref(dark), ctypes.sizeof(dark))
      # Windows 11 also supports explicit caption and title-text colors.
      for attribute, color in ((35, 0x202020), (36, 0xFFFFFF)):
         value = wintypes.DWORD(color)
         set_attribute(handle, attribute, ctypes.byref(value), ctypes.sizeof(value))
   except (OSError, AttributeError):
      pass


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

   t = re.search(r"\((\d+),[ ]*(\d+)\)", dims)
   dims = (int(t.group(1)), int(t.group(2)))

   settings = SettingsMenu(dims, fullscreen)
   screen = setDisplay(dims, settings.fullscreen)

   # Create an instance of the game clock
   gameClock = pygame.time.Clock()

   USER_INTERFACE.setResourcePath(os.path.join("utils","menuButtons.csv"))

   if fileName.endswith(".csv"):
      fileName = fileName[:-4]
      
   game = JeopardyGameGUI(fileName, int(answerTime), dims, LocalPlayers(dims))

   RUNNING = True

   while RUNNING:

      #Increment the clock
      ticks = gameClock.tick(60) / 1000

      screen.fill((255,255,255))

      game.draw(screen)
      settings.draw(screen)
      
      pygame.display.flip()

      # event handling, gets all event from the eventqueue
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            RUNNING = False
            continue
         was_open = settings.open
         action = settings.handle_event(event)
         if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            action = "toggle_fullscreen"
         if action == "toggle_fullscreen":
            try:
               screen = setDisplay(dims, not settings.fullscreen)
               settings.fullscreen = not settings.fullscreen
               settings.message = ""
               settings.save()
            except pygame.error:
               screen = setDisplay(dims, settings.fullscreen)
               settings.message = "Display mode unavailable. Try again."
            if game.multiplayer.setup_open or game.wager is not None:
               pygame.key.start_text_input()
            continue
         if event.type == pygame.KEYDOWN and event.key == pygame.K_m and not game.multiplayer.setup_open:
            SOUNDS.toggleMute()
            continue
         if was_open or settings.open or (event.type == pygame.KEYDOWN and event.key == pygame.K_F1):
            continue
         if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            RUNNING = False
            continue
         game.handleEvent(event)
         if game.new_game_requested:
            game = JeopardyGameGUI(fileName, int(answerTime), dims, LocalPlayers(dims))

      # Keep the current clue paused while the settings panel is open.
      if not settings.open:
         game.update(ticks)

   #Close the pygame window and quit pygame
   settings.save()
   pygame.quit()

def initializeManagers():
   SOUNDS.setResourcePath(os.path.join("resources","data","music.csv"))
   SOUNDS.setMusicFolderPath(os.path.join("resources","music"))

CONTROLS = """
Escape exits. M toggles mute. F1 opens settings. F11 toggles maximized window.
Click a clue to reveal it; Space reveals the answer and advances to the board.
"""

if __name__ == "__main__":
   descStr = "A program that runs a Jeopardy Game with Jeopardy, Double Jeopardy, and Final Jeopardy Rounds"
   parser = argparse.ArgumentParser(description=descStr)
   parser.add_argument("-c", "--controls", dest="controls", action="store_true", default=False,
     help="show game controls and exit")
   parser.add_argument("--questions", dest="qfile",
     default="JEOPARDY_CSV_REAL", type=str, required=False,
     help="the name of the CSV file that contains all of the questions and answers for the Jeopardy Game")
   parser.add_argument("--timer", dest="timer",
     default=30, type=int, required=False,
     help="the amount of time in seconds that players will have to answer questions")
   parser.add_argument("--fullscreen", dest="fullscreen", action="store_true", default=None,
     help="start in a maximized window")
   parser.add_argument("--dims", dest="dims", type=str,
     default="(1200,800)", required=False,
     help="the width and height of the desired screen in pixels : Entered as (<width>, <height>)") 
   args = parser.parse_args()
   if not args.controls:
      main(args.qfile, args.timer, args.fullscreen, args.dims )
   else:
      print(CONTROLS)

