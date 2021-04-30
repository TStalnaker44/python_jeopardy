"""
Author: Trevor Stalnaker
File: button.py

A class that creates and manages a button object
"""

import pygame
from polybius.graphics.utils.textgraphic import TextGraphic
from .multilinetextbox import MultiLineTextBox
from polybius.utils.eventwrapper import EventWrapper

class Button(TextGraphic):

    def __init__(self, text, position, font, fontColor, backgroundColor,
                 height, width, borderColor=(0,0,0), borderWidth=0, antialias=True,
                 control=EventWrapper(pygame.MOUSEBUTTONDOWN, 1, []),
                 curser=pygame.mouse):
        """Initializes the widget with a variety of parameters"""
 
        super().__init__(position, text, font, fontColor, antialias)
        
        self._width = width
        self._height = height
        
        self._backgroundColor = backgroundColor
        self._borderColor = borderColor
        self._borderWidth = borderWidth

        # Current button colors
        self._currentFontColor = fontColor
        self._currentBackgroundColor = backgroundColor

        # Set the controls for interacting with the button
        self._press = control
        self._release = EventWrapper(self._press.getType()+1,
                                     self._press.getKey, [])
        
        # Set the item that interacts with the button (the mouse by default)
        self._curser = curser

        self.updateGraphic()

    def setBackgroundColor(self, backgroundColor):
        """Sets the button's background color"""
        self._backgroundColor = backgroundColor
        self.updateGraphic()

    def setBorderColor(self, color):
        """Sets the button's border color"""
        self._borderColor = borderColor
        self.updateGraphic()

    def setBorderWidth(self, width):
        """Set's the button's border width"""
        self._borderWidth = width
        self.updateGraphic()

    def buttonPressed(self):
        """Updates the button styling when button is pressed"""
        self._currentFontColor = self.shiftRGBValues(self._fontColor,
                                                     (40,40,40))
        self._currentBackgroundColor = self.shiftRGBValues(self._backgroundColor,
                                                            (20,20,20))
        self.updateGraphic()

    def setToDefaultStyling(self):
        """Updates the button to its default style"""
        self._currentBackgroundColor = self._backgroundColor
        self._currentFontColor = self._fontColor
        self.updateGraphic()

    def handleEvent(self, event, func, args=None, offset=(0,0)):
        """Handles events on the button"""
        if args != None and type(args) not in (tuple, list):
            args = (args,)
        rect = self.getCollideRect()
        rect = rect.move(offset[0],offset[1])
        if self._press.check(event):
            if rect.collidepoint(self._curser.get_pos()):
                self.buttonPressed()
                if args == None:
                    func()
                else:
                    func(*args)
        elif self._release.check(event):
                self.setToDefaultStyling()
        elif rect.collidepoint(self._curser.get_pos()):
            self.setHover()
        else:
            self.setToDefaultStyling()
                
    def setHover(self):
        """Updates the button's sytling when the mouse hovers over the button"""
        self._currentBackgroundColor = self.shiftRGBValues(self._backgroundColor,
                                                           (-40,-40,-40))
        self.updateGraphic()

    def internalUpdate(self, surf):
        """Update the button after parameters have been changed"""

        # Use the current background color
        surf.fill(self._currentBackgroundColor)

        # Create and draw the internal textbox
        t = MultiLineTextBox(self._text, (0,0), self._font,
                    self._currentFontColor, antialias=self._antialias)
        t.center(surf)
        t.draw(surf)

