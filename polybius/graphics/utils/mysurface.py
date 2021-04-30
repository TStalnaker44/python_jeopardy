"""
Author: Trevor Stalnaker
File: mysurface.py

A class that converts pygame surfaces to surfaces inheriting from Drawable
"""

from polybius.graphics.utils.abstractgraphic import AbstractGraphic

class MySurface(AbstractGraphic):

    def __init__(self, surface, position=(0,0)):
        """Initializes the MySurface object"""
        super().__init__(position)
        self._image = surface

    def update(self, surface):
        """Updates the MySurface object with a new surface"""
        self._image = surface
