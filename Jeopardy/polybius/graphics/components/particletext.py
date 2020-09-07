"""
Author: Trevor Stalnaker
File: particletext.py

A class that models and manages text that moves and changes in opacity
"""

import pygame
from .multilinetextbox import MultiLineTextBox


class ParticleText():

    def __init__(self, text, startPos, endPos, time, font,
                 fontColor, antialias=True):
        """Initializes the widget with a variety of parameters"""
        self._startPos = startPos
        self._endPos = endPos

        self._text = text
        self._font = font
        self._fontColor = fontColor
        self._antialias = antialias

        self._effectTime = time
        self._effectTimer = self._effectTime
        self._alpha = 0

        xVel = (endPos[0] - startPos[0]) // time
        yVel = (endPos[1] - startPos[1]) // time
        self._velocity = (xVel, yVel)

        self._alphaScale = (255 // time) * 2
        
        self._textBox = MultiLineTextBox(self._text, self._startPos,
                                         self._font, self._fontColor,
                                         antialias=self._antialias)

        self._done = False

    def setText(self, text):
        self._text = text
        self._textBox.setText(text)

    def setFontColor(self, fontColor):
        self._fontColor = fontColor
        self._textBox.setFontColor(fontColor)

    def reverseDirection(self):
        """Reverse the direction of the animation"""
        self._endPos, self._startPos = self._startPos, self._endPos
        xVel = (self._endPos[0] - self._startPos[0]) // self._effectTime
        yVel = (self._endPos[1] - self._startPos[1]) // self._effectTime
        self._velocity = (xVel, yVel)
        self.reset()
        
    def draw(self, surface):
        """Draws the particle text object if its animation is not finished"""
        if not self.finished():
            self._textBox._image.set_alpha(self._alpha)
            self._textBox.draw(surface)

    def finished(self):
        """Return if the animation has finished"""
        return self._done

    def reset(self):
        """Resets the internal timer of the animation"""
        self._done = False
        self._effectTimer = self._effectTime
        self._alpha = 0
        self._textBox.setPosition(self._startPos)
        
    def update(self, ticks):
        """Update the attributes and position of the text based on ticks"""
        
        # Update the position of the textbox
        if self._effectTimer > 0:
            t = self._textBox
            self._textBox.setPosition((t.getX() + (self._velocity[0]*ticks),
                              t.getY() + (self._velocity[1]*ticks)))
            self._effectTimer -= ticks
        else:
            self._done = True
            
        # Update the alpha values of the textbox
        if self._effectTimer > self._effectTime // 2:
            self._alpha += (self._alphaScale * ticks)
        else:
            self._alpha -= (self._alphaScale * ticks)
        
