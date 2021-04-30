"""
Author: Trevor Stalnaker
File: menu.py

A general class for creating menus

Parameters:
    pos - (x,y) position for the top-left corner of the menu
    dims - (width, height) pixels of the menu
    commands - list of dictionaries specifying the button attributes
    padding - (horizontal, vertical) padding between border and buttons
    spacing - space in pixels between buttons
    color - rgb color of the menu background (None for transparent)
    borderColor - rgb color value for border
    borderWidth - pixel width for the border
    font - Supplied as a pygame font
    orientation - "vertical" | "horizontal"
"""

import pygame
from polybius.graphics.components import Button
from polybius.graphics.basics.drawable import Drawable
from polybius.graphics.utils.window import Window

class Menu(Drawable, Window):

    def __init__(self, pos, dims, commands, padding=0, spacing=0,
                 color=(80,80,80), borderColor=(0,0,0),
                 borderWidth=2, orientation="vertical"):
        """Initializes the menu"""

        Drawable.__init__(self, "", pos, worldBound=False)
        Window.__init__(self)

        self._offset = (pos[0], pos[1])

        self._width  = dims[0]
        self._height = dims[1]

        h_padding = padding[0]
        v_padding = padding[1]
            
        self._borderColor = borderColor
        self._borderWidth = borderWidth
        self._backgroundColor = color

        n = len(commands)

        xStart = h_padding
        yStart = v_padding

        self._buttons = []

        # Create buttons with a vertical configuration
        if orientation == "vertical":
            
            buttonWidth  = self._width - (2*h_padding) - (2*borderWidth)
            buttonHeight = (self._height - (2*v_padding) - \
                           ((n-1)*spacing) - (2*borderWidth)) // n
        
            for x, b in enumerate(commands):
                font = pygame.font.SysFont(b["font"], b["fontSize"])
                self._buttons.append((Button(b["text"],
                                         (xStart + self._offset[0],
                                          yStart + (x*buttonHeight) + \
                                          (x*spacing) + self._offset[1]),
                                    font, b["fontColor"], b["color"],
                                    buttonHeight, buttonWidth, b["borderColor"],
                                         b["borderWidth"]),
                                  x+1, b["closeOnPress"], (b.get("toggleText",None),b["text"])))

        # Create buttons with a horizontal configuration
        elif orientation == "horizontal":

            buttonWidth  = (self._width - (2*h_padding) - \
                           ((n-1)*spacing) - (2*borderWidth)) // n
            buttonHeight = self._height - (2*v_padding) - (2*borderWidth)
            
            for x, b in enumerate(commands):
                font = pygame.font.SysFont(b["font"], b["fontSize"])
                self._buttons.append((Button(b["text"],
                                         (xStart + self._offset[0] +\
                                          (x*buttonWidth) + (x*spacing),
                                          yStart + self._offset[1]),
                                    font, b["fontColor"], b["color"],
                                    buttonHeight, buttonWidth, b["borderColor"],
                                         b["borderWidth"]),
                                  x+1, b["closeOnPress"], (b.get("toggleText",None),b["text"])))

        self._selection = None

        self.createDisplay()

    def getButtonByText(self, text):
        """Return the button with the provided text"""
        for button in self._buttons:
            if button[0].getText() == text:
                return button[0]

    def getButtonByPosition(self, position):
        """Return the button at the given position in the menu"""
        return self._buttons[position][0]

    def handleEvent(self, event):
        """Handles events on the pause menu"""
        for b in self._buttons:
            b[0].handleEvent(event,self.select,(b,))
        return self.getSelection()

    def select(self, button):
        """Sets the current selection"""
        b, selection, closeOnPress, toggleText = button
        if closeOnPress:
            self.close()
        if toggleText[0] != None:
            currentText = b._text
            if toggleText[0] == currentText:
                b.setText(toggleText[1])
            else:
                b.setText(toggleText[0])
        self._selection = selection

    def getSelection(self):
        """Returns the current selection and resets it to None"""
        sel = self._selection
        self._selection = None
        return sel

    def draw(self, screen):
        """Draws the menu on the screen"""
        super().draw(screen)
        # Draw buttons
        for b in self._buttons:
            b[0].draw(screen)

    def createDisplay(self):
        """Create the display of the menu"""

        # Draw the border
        surfBack = pygame.Surface((self._width, self._height))
        surfBack.fill(self._borderColor)

        # Draw the background
        surf = pygame.Surface((self._width - (self._borderWidth * 2),
                              self._height - (self._borderWidth * 2)))

        # Apply the background color or make transparent
        if self._backgroundColor == None:
            surf.fill((1,1,1))
            surfBack.set_colorkey((1,1,1))
        else:
            surf.fill(self._backgroundColor)

        # Blit the widget layer onto the back surface
        surfBack.blit(surf, (self._borderWidth, self._borderWidth))
        
        self._image = surfBack
