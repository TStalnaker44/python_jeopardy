"""
Author: Trevor Stalnaker
File: confirmationwindow.py

A class that models and manages a confirmation window
"""

import pygame
from polybius.graphics.utils.textgraphic import TextGraphic
from polybius.graphics.utils.window import Window
from polybius.graphics.components.textbox import TextBox
from polybius.graphics.components.button import Button
from polybius.graphics.components.multilinetextbox import MultiLineTextBox

class ConfirmationWindow(TextGraphic, Window):

    def __init__(self, text, position, dimensions, font, fontColor,
                 backgroundColor, buttonColor, buttonDimensions, buttonFont,
                 buttonFontColor, confirmationText="YES", denialText="NO",
                 buttonBorderWidth=1,buttonBorderColor=(0,0,0), borderWidth=0,
                 borderColor=(0,0,0), antialias=True):
        """Initializes the widget with a variety of parameters"""
        
        TextGraphic.__init__(self, position, text, font, fontColor, antialias)
        Window.__init__(self)
        
        self._height = dimensions[1]
        self._width = dimensions[0]
        
        self._backgroundColor = backgroundColor
        self._borderWidth = borderWidth
        self._borderColor = borderColor

        self._offset = position

        # Create a temporary image to use for initial centering
        self._image = pygame.Surface((self._width, self._height))

        # Create the internal textbox
        self._t = MultiLineTextBox(self._text, (0,0), self._font,
                                       self._fontColor, self._backgroundColor)
        self._t.keepCentered(self, (1/2, 1/4))
        
        # Create the buttons
        self._b1 = Button(confirmationText, (0,0), buttonFont, buttonFontColor,
                         buttonColor,buttonDimensions[1],
                         buttonDimensions[0],buttonBorderColor, buttonBorderWidth)
        self._b1.keepCentered(self, (1/3,3/4))
        
        self._b2 = Button(denialText, (0,0), buttonFont, buttonFontColor,
                         buttonColor,buttonDimensions[1],
                         buttonDimensions[0],buttonBorderColor, buttonBorderWidth)
        self._b2.keepCentered(self, (2/3,3/4))

        self._sel = None

        self.updateGraphic()

    def setText(self, text):
        """Sets the text of the window"""
        self._text = text
        self._t.setText(text)
        self.updateGraphic()

    def setFont(self, font):
        self._font = font
        self._t.setFont(font)
        self.updateGraphic()

    def setFontColor(self, fontColor):
        self._fontColor = fontColor
        self._t.setFontColor(fontColor)
        self.updateGraphic()

    def setAntiAlias(self, antialias):
        self._antialias = antialias
        self._t.setAntiAlias(antialias)
        self._updateGraphic()

    def handleEvent(self, event):
        """Handles events on the window"""
        self._offset = self._position
        self._b1.handleEvent(event,self.confirm,offset=self._offset)
        self._b2.handleEvent(event,self.reject,offset=self._offset)
        self.updateGraphic()
        return self.getSelection()

    def confirm(self):
        """Sets selection to confirm and closes the window"""
        self.close()
        self._sel = 1

    def reject(self):
        """Sets selection to reject and closes the window"""
        self.close()
        self._sel = 0

    def getSelection(self):
        """Returns the current selection and resets the selection to None"""
        sel = self._sel
        self._sel = None
        return sel

    def internalUpdate(self, surf):
        """Update the window after parameters have been changed"""     
        self._t.draw(surf)
        self._b1.draw(surf)
        self._b2.draw(surf)
