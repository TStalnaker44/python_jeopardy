"""
@author: Trevor Stalnaker
File: main.py

The main loop for running Jeopardy Python Edition
"""

import pygame, copy, os, argparse, csv, sqlite3
from polybius.graphics import *
from utils.uiManager import USER_INTERFACE
from polybius.managers import SOUNDS
import utils.jeopardy, re
from utils.questioncard import QuestionCard
from utils.jeopardy_gui import JeopardyGameGUI
from utils.settings import SettingsMenu
from utils.localplayers import LocalPlayers
from utils.gamelibrary import GameLibrary
from utils.progress import ProgressStore
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


def main(fileName, answerTime, fullscreen, dims, show_library=False):
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
      
   progress = ProgressStore(settings.path.with_name("study-progress.sqlite3"))
   library = GameLibrary(dims, fileName, settings.path.with_name("library.json"), progress=progress) if show_library else None
   game = None if library else JeopardyGameGUI(fileName, int(answerTime), dims, LocalPlayers(dims), progress)

   RUNNING = True

   while RUNNING:

      #Increment the clock
      ticks = gameClock.tick(60) / 1000

      screen.fill((255,255,255))

      if library is not None and library.open:
         library.draw(screen, game is not None)
      elif game is not None:
         game.draw(screen)
         if library is not None:
            library.draw_navigation(screen)
      settings.draw(screen)
      
      pygame.display.flip()

      # event handling, gets all event from the eventqueue
      force_save = False
      for event in pygame.event.get():
         if event.type in (pygame.KEYDOWN, pygame.TEXTINPUT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.QUIT):
            force_save = True
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
            if game is not None and (game.multiplayer.setup_open or game.wager is not None) and not (library and library.open):
               pygame.key.start_text_input()
            continue
         if event.type == pygame.KEYDOWN and event.key == pygame.K_m and not (
            game is not None and game.multiplayer.setup_open and not (library and library.open)
         ):
            SOUNDS.toggleMute()
            continue
         if was_open or settings.open or (event.type == pygame.KEYDOWN and event.key == pygame.K_F1):
            continue
         if library is not None:
            library_was_open = library.open
            action = library.handle_event(event, game is not None)
            if action in ("start", "resume_saved", "restart"):
               if game is not None and not game.save_checkpoint(True):
                  library.message = game.checkpoint_error
                  continue
               selected_file = str(library.selected_entry["path"].with_suffix(""))
               try:
                  entry = library.selected_entry
                  if action == "start":
                     new_game = JeopardyGameGUI(selected_file, int(answerTime), dims, LocalPlayers(dims), progress, entry["game_id"], entry["title"])
                  else:
                     saved = progress.load_checkpoint(entry["game_id"])
                     if saved is None:
                        raise ValueError("No saved game is available. Refresh the library to start a new game.")
                     new_game = JeopardyGameGUI.from_checkpoint(saved, dims, progress, restart=action == "restart")
               except (OSError, ValueError, csv.Error, sqlite3.Error, KeyError, TypeError) as error:
                  library.message = str(error)
                  pygame.key.stop_text_input()
               else:
                  game = new_game
                  fileName = selected_file
                  library.remember()
                  library.open = False
            elif action == "resume":
               library.open = False
               if game.multiplayer.setup_open or game.wager is not None:
                  pygame.key.start_text_input()
            elif action == "quit":
               RUNNING = False
            if library_was_open or library.open:
               continue
         if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            RUNNING = False
            continue
         if game is not None:
            game.handleEvent(event)
            if game.new_game_requested:
               if library is not None:
                  game.new_game_requested = False
                  library.open = True
                  library.refresh()
                  pygame.key.stop_text_input()
               else:
                  game = JeopardyGameGUI(fileName, int(answerTime), dims, LocalPlayers(dims), progress)
            
      # Keep the current clue paused while the settings panel is open.
      if game is not None and not settings.open and not (library and library.open):
         game.update(ticks)
      if game is not None:
         if not game.save_checkpoint(force_save or not RUNNING):
            RUNNING = True
            if library is not None and library.open:
               library.message = game.checkpoint_error
                   
   #Close the pygame window and quit pygame
   settings.save()
   progress.close()
   pygame.quit()

def initializeManagers():
   SOUNDS.setResourcePath(os.path.join("resources","data","music.csv"))
   SOUNDS.setMusicFolderPath(os.path.join("resources","music"))

CONTROLS = """
Controls:

- Press the ESCAPE key or press the X to exit the game

- Hit the M key to mute and unmute game audio

- Click Settings or press F1 to adjust volume and fullscreen

- Press F11 to toggle fullscreen

- Choose a question set from the library at startup; use Library or F2 to return

- Add CSV imports a new question set into your library

- Played/completed counts and question results save automatically

- Select a game and choose Review answers to see correct, wrong and skipped history

- Click on Question Tiles to select them

   - The timer will begin automatically

- Click the Space Bar when the question has been answered to advance
   to the solution screen. 

   - The game will advance automatically when the timer runs out

- Click the Space Bar once more to advance from the Answer Screen
   back to the Game Board

- The game will automatically advance between rounds

- Add up to six players or teams at startup, or choose Play solo

- After revealing an answer, use C for correct, W for incorrect, or S to skip

- Turns advance after each clue. Click a player on the board to change turns

- Enter a wager before a Daily Double is revealed

- Enter each player's Final Jeopardy wager after the category is shown

- Correct and incorrect answers add or subtract the entered wager
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
      main(args.qfile, args.timer, args.fullscreen, args.dims, show_library=True)
   else:
      print(CONTROLS)

