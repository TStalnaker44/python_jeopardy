"""
Author: Trevor Stalnaker
File: banner.py

A class that creates and manages a banner
"""

from polybius.graphics.utils.abstractgraphic import AbstractGraphic
import pygame

class Banner(AbstractGraphic):

    def __init__(self, position, color, dimensions, borderColor=(0,0,0), borderWidth=0):
        """Initializes the widget with a variety of parameters"""
        super().__init__(position)
        self._backgroundColor = color
        self._height = dimensions[0]
        self._width = dimensions[1]
        self._borderColor = borderColor
        self._borderWidth = borderWidth

        # Create the banner
        self.updateGraphic()
